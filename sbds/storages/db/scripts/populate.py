# -*- coding: utf-8 -*-
import asyncio
import itertools as it
import os
from functools import partial
import aiopg.sa
import asyncpg
import click

from asyncio import Queue

import aiofiles
import uvloop
from tqdm import tqdm
import psycopg2
import funcy

from sqlalchemy.engine.url import make_url
import rapidjson as json
import structlog
import aiohttp

from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from aiohttp.connector import TCPConnector
import asyncpg.exceptions

from sbds.storages.db.tables.async_core import prepare_raw_block_for_storage
from sbds.storages.db.tables.operations import op_db_table_for_type
from sbds.storages.db.tables.async_core import prepare_raw_operation_for_storage
from sbds.storages.db.tables import Base
from sbds.storages.db.tables.meta.accounts import extract_account_names

from sbds.storages.db.tables import init_tables
from sbds.storages.db.tables import test_connection
from sbds.storages.db.utils import isolated_engine

from sbds.storages.fs.utils import key as fs_key

from sbds.utils import chunkify

import sbds.sbds_logging

# pylint: skip-file
logger = structlog.get_logger(__name__)

TOTAL_TASKS = 7

STATEMENT_CACHE = {
    'account': 'INSERT INTO sbds_meta_accounts (name) VALUES($1) ON CONFLICT DO NOTHING',
    'block': 'INSERT INTO sbds_core_blocks (raw, block_num, previous, timestamp, witness, witness_signature, transaction_merkle_root) VALUES ($1, $2, $3, $4, $5, $6, $7) ON CONFLICT DO NOTHING'
}

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


pbar_kwargs = dict(
    color=True,
    show_eta=False,
    show_percent=False,
    empty_char='░',
    fill_char='█',
    show_pos=True,
    bar_template='%(bar)s  %(info)s')


def get_op_insert_stmt(prepared_op, db_tables):
    stmt = STATEMENT_CACHE.get('type')
    if stmt:
        return stmt
    op_type = prepared_op['operation_type']
    table = db_tables[op_db_table_for_type(op_type)]
    values_str = ', '.join(
        f'${i}' for i in range(1, len(prepared_op.keys()) + 1))
    columns_str = ', '.join(f'"{k}"' for k in prepared_op.keys())
    STATEMENT_CACHE[op_type] = f'INSERT INTO {table} ({columns_str}) VALUES({values_str}) ON CONFLICT DO NOTHING'
    return STATEMENT_CACHE[op_type]


def create_async_engine(database_url, loop=None, minsize=40, maxsize=50, **kwargs):
    sa_db_url = make_url(database_url)
    loop = loop or asyncio.get_event_loop()
    async_engine = loop.run_until_complete(
        aiopg.sa.create_engine(
            user=sa_db_url.username,
            password=sa_db_url.password,
            host=sa_db_url.host,
            port=sa_db_url.port,
            dbname=sa_db_url.database,
            minsize=minsize,
            maxsize=maxsize,
            **kwargs))
    return async_engine


def create_asyncpg_pool(database_url, loop=None, min_size=40, max_size=40, **kwargs):
    loop = loop or asyncio.get_event_loop()
    return loop.run_until_complete(asyncpg.create_pool(database_url,
                                                       min_size=min_size,
                                                       max_size=max_size,
                                                       **kwargs))


def as_completed_limit_concurrent(coros_or_futures, concurrency_limit):
    futures = [
        asyncio.ensure_future(c)
        for c in it.islice(coros_or_futures, 0, concurrency_limit)
    ]

    async def next_done():
        while True:
            await asyncio.sleep(0)
            for f in futures:
                if f.done():
                    futures.remove(f)
                    try:
                        new_future = next(coros_or_futures)
                        futures.append(
                            asyncio.ensure_future(new_future))
                    except StopIteration:
                        pass
                    return f.result()
    while len(futures) > 0:
        yield next_done()


def fmt_success_message(msg, *args):
    base_msg = msg % args
    return '{success} {msg}'.format(
        success=click.style('success', fg='green'), msg=base_msg)


def fmt_task_message(task_msg,
                     emoji_code_point=None,
                     show_emoji=None,
                     task_num=None,
                     total_tasks=TOTAL_TASKS):

    show_emoji = show_emoji or os.sys.platform == 'darwin'
    _emoji = ''
    if show_emoji:
        _emoji = emoji_code_point

    return '[{task_num}/{total_tasks}] {task_emoji}  {task_msg}...'.format(
        task_num=task_num,
        total_tasks=total_tasks,
        task_emoji=_emoji,
        task_msg=task_msg)


def get_account_names(url):
    import requests
    RequestsSession = requests.Session()
    lower_bound_name = 'a'
    limit = 1000
    accts = list()
    try:
        while True:
            resp = RequestsSession.post(
                url,
                json={
                    'id': 1,
                    'jsonrpc': '2.0',
                    'method': 'lookup_accounts',
                    'params': [
                        lower_bound_name,
                        limit]})
            accounts_in_resp = resp.json()['result']
            accts.extend(accounts_in_resp)
            if lower_bound_name == accounts_in_resp[-1]:
                break
            lower_bound_name = accounts_in_resp[-1]
    except Exception as e:
        print(e)
    return sorted(list(set(accts)))


async def preload_account_names(pool, account_names):
    non_blank_account_names = (a for a in account_names if a not in ('', None))
    unique_account_names = set(non_blank_account_names)
    account_name_records = [(a,) for a in unique_account_names]
    async with pool.acquire() as conn:
        try:
            await conn.copy_records_to_table('sbds_meta_accounts', records=account_name_records)
        except Exception as e:
            logger.exception('error preloading account names', e=e)


def task_confirm_db_connectivity(database_url):
    url, table_count = test_connection(database_url)

    if url:
        success_msg = fmt_success_message(
            'connected to %s and found %s tables', url.__repr__(), table_count)
        click.echo(success_msg)

    if not url:
        raise Exception('Unable to connect to database')


def task_init_db_if_required(database_url):

    init_tables(database_url, Base.metadata)


def task_load_db_meta(database_url):
    with isolated_engine(database_url) as engine:
        from sqlalchemy import MetaData
        m = MetaData()
        m.reflect(bind=engine)
    return m


def is_name_missing_from_accounts_error(e):
    # Key (worker_account)=(kevtorin) is not present in table "sbds_meta_accounts"
    err_str = e.detail
    return 'is not present in table "sbds_meta_accounts"' in err_str


def missing_account_name_from_error(e):
    return e.detail.split('=')[1].split(')')[0].replace('(', '')  # hehe


async def get_existing_and_missing_count(engine, start_block, end_block):
    async with engine.acquire() as conn:
        existing_count = await conn.fetchval('SELECT COUNT(*) from sbds_core_blocks WHERE block_num >=$1 AND block_num <= $2', start_block, end_block)
    range_count = len(range(start_block, end_block + 1))
    missing_count = range_count - existing_count
    return existing_count, missing_count, range_count


async def get_latest_db_block_num(engine):
    async with engine.acquire() as conn:
        last_block_num = await conn.scalar('SELECT MAX(block_num) from sbds_core_blocks')
    return last_block_num


async def get_last_irreversible_block_num(url, client):
    response = await client.post(url, data=f'{{"id":1,"jsonrpc":"2.0","method":"get_dynamic_global_properties"}}'.encode())
    jsonrpc_response = await response.json()
    return jsonrpc_response['result']['last_irreversible_block_num']


async def collect_missing_block_nums(engine, last_chain_block, missing_count, start_block=None, pbar=None):
    BLOCKNUM_CHUNK_SEARCH_SIZE = 10_000
    start_block = start_block or 1
    complete_block_nums = range(start_block, last_chain_block + 1)

    if missing_count == last_chain_block:
        return complete_block_nums
    missing_block_nums = set(complete_block_nums)
    query = 'SELECT block_num from sbds_core_blocks WHERE block_num>=$1'

    async with engine.acquire() as conn:
        async with conn.transaction():
            cursor = await conn.cursor(query, start_block)
            while True:
                rows = await cursor.fetch(BLOCKNUM_CHUNK_SEARCH_SIZE)
                if not rows:
                    break
                missing_block_nums.difference_update(set(b[0] for b in rows))
                if pbar:
                    pbar.update(BLOCKNUM_CHUNK_SEARCH_SIZE)
    pbar.update(len(missing_block_nums))
    return missing_block_nums


# --- Blocks ---
async def fetch_blocks_and_ops_in_blocks(url, client, block_nums):
    request_data = ','.join(
        f'{{"id":{block_num},"jsonrpc":"2.0","method":"get_block","params":[{block_num}]}},{{"id":{block_num},"jsonrpc":"2.0","method":"get_ops_in_block","params":[{block_num},false]}}'
        for block_num in block_nums)
    request_json = f'[{request_data}]'.encode()
    response = 'n/a'
    while True:
        try:
            response = await client.post(url, data=request_json)
            jsonrpc_response = await response.json()
            response_pairs = funcy.partition(2, jsonrpc_response)
            results = []
            for get_block, get_ops in response_pairs:
                assert get_block['id'] == get_ops['id']
                results.append((get_block['id'], get_block['result'], get_ops['result']))
            assert len(results) == len(block_nums)
            return results
        except Exception as e:
            logger.exception('error fetching ops in block',
                             e=e, response=response)


async def local_fetch_blocks_and_ops_in_blocks(local_path, block_nums):
    results = []
    for block_num in block_nums:
        base = None
        try:
            base = fs_key(block_num, base_path=local_path)
            with aiofiles.open(f'{base}/block.json') as f:
                raw_block = await f.read()
            with aiofiles.open(f'{base}/ops.json') as f:
                raw_ops = await f.read()
            block = json.loads(raw_block)
            ops = json.loads(raw_ops)
            results.append((block_num, block, ops))
            return results
        except Exception as e:
            logger.exception('error fetching block and/or ops in block ',
                             e=e, base=base)


async def safe_store_block_and_ops(pool, db_tables, prepared_block, prepared_ops):
    """Atomic add block,operations, and virtual operations in block



    :param pool:
    :param db_tables:
    :param prepared_block:
    :param prepared_ops:
    :return:
    """

    raw_add_account_stmt = STATEMENT_CACHE['account']
    raw_stmts = [(STATEMENT_CACHE['block'], prepared_block.values())]

    # collect all account names referenced in block and ops
    account_names_in_ops = extract_account_names(prepared_ops)
    account_names_in_ops.add(prepared_block['witness'])
    account_name_records = [(a,) for a in account_names_in_ops]

    for prepared_op in prepared_ops:
        raw_stmts.append((get_op_insert_stmt(prepared_op, db_tables), prepared_op.values()))

    async with pool.acquire() as conn:
        prepared_stmts = [await conn.prepare(stmt) for stmt, _ in raw_stmts]
        add_acct_stmt = await conn.prepare(raw_add_account_stmt)

        stmts = zip(prepared_stmts, (vals for _, vals in raw_stmts))
        async with conn.transaction():
            # add accounts first
            await conn.executemany(raw_add_account_stmt, account_name_records)

        async with conn.transaction():
            # add block and ops
            for i, stmt in enumerate(stmts):
                query, args = stmt
                while True:
                    stmt_tr = conn.transaction()
                    await stmt_tr.start()
                    try:
                        await query.fetchval(*args)
                        await stmt_tr.commit()
                        break
                    except (asyncpg.exceptions.ForeignKeyViolationError) as e:
                        await stmt_tr.rollback()
                        if is_name_missing_from_accounts_error(e):
                            missing_account_name = missing_account_name_from_error(
                                e)
                            stmt2_tr = conn.transaction()
                            await stmt2_tr.start()
                            await add_acct_stmt.fetchval(missing_account_name)
                            await stmt2_tr.commit()
                        else:
                            if i == 0:
                                prepared = prepared_block
                            else:
                                prepared = prepared_ops[i - 1]
                            logger.exception('error storing block and ops',
                                             e=e,
                                             accts=account_names_in_ops,
                                             prepared=prepared,
                                             stmt=stmt)
                            raise e
                    except Exception as e:
                        await stmt_tr.rollback()
                        if i == 0:
                            prepared = prepared_block
                        else:
                            prepared = prepared_ops[i - 1]
                        logger.exception('error storing block and ops',
                                         e=e,
                                         accts=account_names_in_ops,
                                         prepared=prepared,
                                         stmt=stmt,
                                         type=prepared.get('operation_type'))
                        raise e


async def store_block_and_ops(pool, db_tables, prepared_block, prepared_ops):
    """Atomic add block,operations, and virtual operations in block



    :param pool:
    :param db_tables:
    :param prepared_block:
    :param prepared_ops:
    :return:
    """

    raw_add_account_stmt = STATEMENT_CACHE['account']
    raw_stmts = [(STATEMENT_CACHE['block'], prepared_block.values())]

    # collect all account names referenced in block and ops
    #account_names_in_ops = extract_account_names(prepared_ops)
    # account_names_in_ops.add(prepared_block['witness'])
    #account_name_records = [(a,) for a in account_names_in_ops ]

    for prepared_op in prepared_ops:
        raw_stmts.append((get_op_insert_stmt(prepared_op, db_tables), prepared_op.values()))

    async with pool.acquire() as conn:
        prepared_stmts = [await conn.prepare(stmt) for stmt, _ in raw_stmts]
        stmts = zip(prepared_stmts, (vals for _, vals in raw_stmts))

        async with conn.transaction():
            # await conn.executemany(raw_add_account_stmt, account_name_records)
            # add block and ops
            for i, stmt in enumerate(stmts):
                query, args = stmt
                try:
                    await query.fetchval(*args)
                except Exception as e:
                    if i == 0:
                        prepared = prepared_block
                    else:
                        prepared = prepared_ops[i - 1]
                    logger.exception('error storing block and ops',
                                     e=e,
                                     # accts=account_names_in_ops,
                                     prepared=prepared,
                                     stmt=stmt,
                                     type=prepared.get('operation_type'))
                    raise e


async def process_block(block_num, raw_block, raw_ops, pool, db_tables, blocks_pbar=None, ops_pbar=None):
    prepared_futures = [prepare_raw_block_for_storage(raw_block, loop=loop)]
    if raw_ops:
        prepared_futures.extend(prepare_raw_operation_for_storage(raw_op, loop=loop)
                                for raw_op in raw_ops)
    prepared = await asyncio.gather(*prepared_futures)
    prepared_block = prepared[0]
    if raw_ops:
        prepared_ops = prepared[1:]
    else:
        prepared_ops = []
    await store_block_and_ops(pool, db_tables, prepared_block, prepared_ops)
    blocks_pbar.update()
    if len(raw_ops) < 50:
        ops_pbar.total = ops_pbar.total - (50 - len(raw_ops))
    ops_pbar.update(len(raw_ops))
    return (block_num, raw_block, prepared_block, raw_ops, prepared_ops)


async def process_block_chunk(block_num_batch, url, client, engine, db_tables, blocks_pbar=None, ops_pbar=None):
    results = await fetch_blocks_and_ops_in_blocks(url, client, block_num_batch)
    block_futures = [process_block(
        block_num,
        raw_block,
        raw_ops_in_block,
        engine,
        db_tables,
        blocks_pbar=blocks_pbar,
        ops_pbar=ops_pbar) for block_num, raw_block, raw_ops_in_block in results if raw_block and raw_ops_in_block]
    return await asyncio.wait(block_futures)


async def process_blocks(missing_block_nums, url, client, pool, db_meta, blocks_pbar=None, ops_pbar=None):
    CONCURRENCY_LIMIT = 5
    BATCH_SIZE = 10

    db_tables = db_meta.tables
    block_num_batches = chunkify(missing_block_nums, BATCH_SIZE)
    futures = (
        process_block_chunk(
            block_num_batch,
            url,
            client,
            pool,
            db_tables,
            blocks_pbar=blocks_pbar,
            ops_pbar=ops_pbar) for block_num_batch in block_num_batches)

    for results_future in as_completed_limit_concurrent(futures, CONCURRENCY_LIMIT):
        results = await results_future


# --- Operations ---

async def prepare_operation_for_storage(raw_operation):
    return await prepare_raw_operation_for_storage(raw_operation)


async def task_stream_blocks(engine, steemd_http_url, client):
    while True:
        tasks = [
            get_last_irreversible_block_num(steemd_http_url, client),
            get_latest_db_block_num(engine)
        ]
        done, pending = await asyncio.wait(tasks)


@click.command()
@click.option(
    '--database_url',
    type=str,
    envvar='DATABASE_URL',
    help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default'
)
@click.option(
    '--legacy_database_url',
    type=str,
    envvar='LEGACY_DATABASE_URL',
    help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default'
)
@click.option(
    '--steemd_http_url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    help='Steemd HTTP server URL')
@click.option('--start_block', type=int, default=1)
@click.option('--end_block', type=int, default=-1)
@click.option('--accounts_file', type=click.Path(dir_okay=False, exists=True))
def populate(database_url, legacy_database_url, steemd_http_url,
             start_block, end_block, accounts_file):
    _populate(
        database_url,
        legacy_database_url,
        steemd_http_url,
        start_block,
        end_block,
        accounts_file)


def _populate(database_url, legacy_database_url, steemd_http_url,
              start_block, end_block, accounts_file):
    CONNECTOR = TCPConnector(loop=loop, limit=100)
    AIOHTTP_SESSION = aiohttp.ClientSession(loop=loop,
                                            connector=CONNECTOR,
                                            json_serialize=json.dumps,
                                            headers={'Content-Type': 'application/json'})
    DB_META = task_load_db_meta(legacy_database_url)

    try:

        pool = create_asyncpg_pool(database_url)
        task_num = 0
        # [1/7] confirm db connectivity
        task_num += 1
        task_message = fmt_task_message(
            'Confirm database connectivity',
            emoji_code_point=u'\U0001F4DE',
            task_num=task_num)
        click.echo(task_message)
        # task_confirm_db_connectivity(database_url)

        # [2/7] init db if required
        task_num += 1
        task_message = fmt_task_message(
            'Initialising db if required',
            emoji_code_point=u'\U0001F50C',
            task_num=task_num)
        click.echo(task_message)
        task_init_db_if_required(database_url=database_url)

        # [3/7] find last irreversible block
        task_num += 1
        if end_block == -1:
            task_message = fmt_task_message(
                'Finding highest blockchain block',
                emoji_code_point='\U0001F50E',
                task_num=task_num)
            click.echo(task_message)
            last_chain_block_num = loop.run_until_complete(
                get_last_irreversible_block_num(steemd_http_url, AIOHTTP_SESSION))
            end_block = last_chain_block_num
            success_msg = fmt_success_message(
                'last irreversible block number is %s', last_chain_block_num)
            click.echo(success_msg)
        else:
            task_message = fmt_task_message(
                f'Using --end_block {end_block} as highest blockchain block to load',
                emoji_code_point='\U0001F50E',
                task_num=task_num)
            click.echo(task_message)

        # [4/7] build list of blocks missing from db
        existing_count, missing_count, range_count = loop.run_until_complete(
            get_existing_and_missing_count(pool, start_block, end_block))
        task_message = fmt_task_message(
            f'Building list of {missing_count} blocks missing from db between {start_block}<<-->>{end_block}',
            emoji_code_point=u'\U0001F52D',
            task_num=4)
        click.echo(task_message)

        with click.progressbar(length=end_block, **pbar_kwargs) as pbar:
            pbar.update(existing_count)
            missing_block_nums = loop.run_until_complete(
                collect_missing_block_nums(
                    pool,
                    end_block,
                    missing_count,
                    start_block=start_block,
                    pbar=pbar))

        # [5.1/7] preload accounts file
        if accounts_file:
            task_message = fmt_task_message(
                'Preloading account names',
                emoji_code_point=u'\U0001F52D',
                task_num=5)
            click.echo(task_message)
            with open(accounts_file) as f:
                account_names = json.load(f)
            loop.run_until_complete(
                preload_account_names(pool, account_names))
            del account_names

        # [5/7] add missing blocks and operations
        task_message = fmt_task_message(
            'Adding missing blocks and operations to db',
            emoji_code_point=u'\U0001F52D',
            task_num=5)
        click.echo(task_message)

        blocks_progress_bar = tqdm(initial=existing_count,
                                   total=range_count,
                                   bar_format='{bar}| [{rate_fmt}{postfix}]',
                                   ncols=48,
                                   dynamic_ncols=False,
                                   unit=' blocks',
                                   )
        ops_progress_bar = tqdm(initial=existing_count * 50,
                                total=range_count * 50,
                                bar_format='{bar}| [{rate_fmt}{postfix}]',
                                ncols=48,
                                dynamic_ncols=False,
                                unit='    ops')

        loop.run_until_complete(process_blocks(missing_block_nums,
                                               steemd_http_url,
                                               AIOHTTP_SESSION,
                                               pool,
                                               DB_META,
                                               blocks_pbar=blocks_progress_bar,
                                               ops_pbar=ops_progress_bar))

        # [6/7] Make second sweep for missing blocks
        task_message = fmt_task_message(
            'Adding missing blocks and operations to db (second sweep)',
            emoji_code_point=u'\U0001F52D',
            task_num=6)
        click.echo(task_message)

        existing_count, missing_count, range_count = loop.run_until_complete(
            get_existing_and_missing_count(pool, start_block, end_block))
        task_message = fmt_task_message(
            f'Building list of {missing_count} blocks missing from db between {start_block}<<-->>{end_block}',
            emoji_code_point=u'\U0001F52D',
            task_num=4)
        click.echo(task_message)

        with click.progressbar(length=end_block, **pbar_kwargs) as pbar:
            pbar.update(existing_count)
            missing_block_nums = loop.run_until_complete(
                collect_missing_block_nums(
                    pool,
                    end_block,
                    missing_count,
                    start_block=start_block,
                    pbar=pbar))

        blocks_progress_bar = tqdm(initial=existing_count,
                                   total=range_count,
                                   dynamic_ncols=False,
                                   unit=' blocks',
                                   )
        ops_progress_bar = tqdm(initial=existing_count * 50,
                                total=range_count * 50,
                                dynamic_ncols=False,
                                unit='    ops')
        loop.run_until_complete(process_blocks(missing_block_nums,
                                               steemd_http_url,
                                               AIOHTTP_SESSION,
                                               pool,
                                               DB_META,
                                               blocks_pbar=blocks_progress_bar,
                                               ops_pbar=ops_progress_bar))

        # [7/7] stream new blocks
        task_message = fmt_task_message(
            'Streaming blocks', emoji_code_point=u'\U0001F4DD',
            task_num=7)
        click.echo(task_message)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception('ERROR')
        raise e


# included only for debugging with pdb, all the above code should be called
# using the click framework
if __name__ == '__main__':
    populate()
