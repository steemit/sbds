# -*- coding: utf-8 -*-
import asyncio
import itertools as it
import os

import aiopg.sa
import asyncpg
import click

import zmq
import zmq.asyncio
import uvloop
from tqdm import tqdm

import funcy

from sqlalchemy.engine.url import make_url
import rapidjson as json
import structlog
import aiohttp

from aiohttp.connector import TCPConnector
import asyncpg.exceptions

from sbds.storages.db.tables import Base
from sbds.storages.db.tables import init_tables
from sbds.storages.db.tables import test_connection
from sbds.storages.db.utils import isolated_engine
from sbds.utils import chunkify

import sbds.sbds_logging

# pylint: skip-file
logger = structlog.get_logger(__name__)

TOTAL_TASKS = 7


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


async def task_preload_account_names(pool, account_names):
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


async def get_highest_db_block_num(engine):
    async with engine.acquire() as conn:
        last_block_num = await conn.scalar('SELECT MAX(block_num) from sbds_core_blocks')
    return last_block_num


async def get_last_irreversible_block_num(url, client):
    response = await client.post(url, data=f'{{"id":1,"jsonrpc":"2.0","method":"get_dynamic_global_properties"}}'.encode())
    jsonrpc_response = await response.json()
    return jsonrpc_response['result']['last_irreversible_block_num']


async def collect_missing_block_nums(engine, end_block, missing_count, start_block=None, pbar=None):
    start_block = start_block or 1
    complete_block_nums = range(start_block, end_block + 1)

    if missing_count == end_block:
        return complete_block_nums

    query = '''
    SELECT generate_series($1::int,$2::int)
    EXCEPT
    SELECT block_num from sbds_core_blocks where block_num BETWEEN $3 AND $4;
    '''

    async with engine.acquire() as conn:
        results = await conn.fetch(query, start_block, end_block, start_block, end_block)

    return [r[0] for r in results]


async def process_blocks(missing_block_nums,
                         ventilator_send,
                         results_receiver,
                         control_sender,
                         concurrency,
                         jsonrpc_batch_size,
                         blocks_pbar=None,
                         ops_pbar=None):
    CONCURRENCY_LIMIT = concurrency
    BATCH_SIZE = jsonrpc_batch_size

    block_num_batches = chunkify(missing_block_nums, BATCH_SIZE)
    for i in range(CONCURRENCY_LIMIT + 1):
        await ventilator_send.send_json(next(block_num_batches))

    for block_num_batch in block_num_batches:
        events = await results_receiver.poll(timeout=1)
        if events:
            results = await results_receiver.recv_json()
            #logger.info('received results', results=results)
            blocks_pbar.update(len(results))
            await ventilator_send.send_json(block_num_batch)
            #logger.info('work sent')


async def task_stream_blocks(engine, steemd_http_url, client):
    while True:
        tasks = [
            get_last_irreversible_block_num(steemd_http_url, client),
            get_highest_db_block_num(engine)
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
    help='Database connection URL in RFC-1738 format, read from "LEGACY_DATABASE_URL" ENV var by default'
)
@click.option(
    '--steemd_http_url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    help='Steemd HTTP server URL')
@click.option('--start_block', type=click.INT, default=1)
@click.option('--end_block', type=click.INT, default=-1)
@click.option('--accounts_file', type=click.Path(dir_okay=False, exists=True))
@click.option('--concurrency', type=click.INT, default=5)
@click.option('--jsonrpc_batch_size', type=click.INT, default=300)
def populate(database_url, legacy_database_url, steemd_http_url,
             start_block, end_block, accounts_file, concurrency, jsonrpc_batch_size):
    _populate(
        database_url,
        legacy_database_url,
        steemd_http_url,
        start_block,
        end_block,
        accounts_file,
        concurrency,
        jsonrpc_batch_size)


def _populate(database_url, legacy_database_url, steemd_http_url,
              start_block, end_block, accounts_file, concurrency, jsonrpc_batch_size):

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
                task_preload_account_names(pool, account_names))
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

        context = zmq.asyncio.Context()

        # Set up a channel to send work
        ventilator_send = context.socket(zmq.PUSH)
        ventilator_send.bind("tcp://127.0.0.1:5557")

        results_receiver = context.socket(zmq.PULL)
        results_receiver.bind("tcp://127.0.0.1:5558")

        # Set up a channel to send control commands
        control_sender = context.socket(zmq.PUB)
        control_sender.bind("tcp://127.0.0.1:5559")

        loop.run_until_complete(process_blocks(missing_block_nums,
                                               ventilator_send,
                                               results_receiver,
                                               control_sender,
                                               concurrency,
                                               jsonrpc_batch_size))

        # [7/7] stream new blocks
        task_message = fmt_task_message(
            'Streaming blocks', emoji_code_point=u'\U0001F4DD',
            task_num=7)
        click.echo(task_message)

    except KeyboardInterrupt as e:
        raise
    except Exception as e:
        logger.exception('ERROR')
        raise e
    finally:
        control_sender.send("FINISHED")


# included only for debugging with pdb, all the above code should be called
# using the click framework
if __name__ == '__main__':
    populate()
