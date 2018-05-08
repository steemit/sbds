# -*- coding: utf-8 -*-
import asyncio
import asyncio.queues
import functools
import itertools as it
import multiprocessing
import os
import time

from collections import deque
from concurrent.futures import ProcessPoolExecutor


import aiohttp
import asyncpg
import asyncpg.exceptions
import funcy
import rapidjson as json
import structlog

from aiohttp.connector import TCPConnector
from tqdm import tqdm

import sbds.sbds_json

from sbds.storages.db.tables.async_core import prepare_raw_block_for_storage
from sbds.storages.db.tables.async_core import prepare_raw_operation_for_storage
from sbds.storages.db.tables.operations import combined_ops_db_table_map
from sbds.storages.db.utils import isolated_engine

from sbds.utils import chunkify


logger = structlog.get_logger(__name__)
m = multiprocessing.Manager()
RESULTS_Q = m.Queue()

STATEMENT_CACHE = {
    'account': 'INSERT INTO sbds_meta_accounts (name) VALUES($1) ON CONFLICT DO NOTHING',
    'block': 'INSERT INTO sbds_core_blocks (raw, block_num, previous, timestamp, witness, witness_signature, transaction_merkle_root,accounts,op_types) VALUES ($1, $2, $3, $4, $5, $6, $7,$8,$9) ON CONFLICT DO NOTHING'
}


def get_op_insert_stmt(prepared_op):
    stmt = STATEMENT_CACHE.get('type')
    if stmt:
        return stmt
    op_type = prepared_op['operation_type']
    table = combined_ops_db_table_map[op_type]
    values_str = ', '.join(
        f'${i}' for i in range(1, len(prepared_op.keys()) + 1))
    columns_str = ', '.join(f'"{k}"' for k in prepared_op.keys())
    STATEMENT_CACHE[op_type] = f'INSERT INTO {table} ({columns_str}) VALUES({values_str}) ON CONFLICT DO NOTHING'
    #logger.debug('get_op_insert_stmt', op_type=op_type, statement=STATEMENT_CACHE[op_type])
    return STATEMENT_CACHE[op_type]


async def init_conn(conn):
    # logger.debug('init_conn')
    await conn.set_type_codec(
        'jsonb',
        encoder=sbds.sbds_json.dumps,
        decoder=sbds.sbds_json.loads,
        schema='pg_catalog'
    )
    #logger.debug('init_conn set jsonb type codec' )
    await conn.set_type_codec(
        'json',
        encoder=sbds.sbds_json.dumps,
        decoder=sbds.sbds_json.loads,
        schema='pg_catalog'
    )
    #logger.debug('init_conn set json type codec')


def create_asyncpg_pool(database_url, loop=None, max_size=10, **kwargs):
    loop = loop or asyncio.get_event_loop()
    return loop.run_until_complete(asyncpg.create_pool(database_url,
                                                       max_size=max_size,
                                                       init=init_conn,
                                                       **kwargs))


def split_into_num_chunks(seq=None, num_chunks=None):
    return [seq[i::num_chunks] for i in range(num_chunks)]


def load_db_meta(database_url):
    with isolated_engine(database_url) as engine:
        from sqlalchemy import MetaData
        m = MetaData()
        m.reflect(bind=engine)
    return m


# --- Blocks ---
async def fetch_blocks_and_ops_in_blocks(url, client, block_nums):
    request_data = ','.join(
        f'{{"id":{block_num},"jsonrpc":"2.0","method":"get_block","params":[{block_num}]}},{{"id":{block_num},"jsonrpc":"2.0","method":"get_ops_in_block","params":[{block_num},false]}}'
        for block_num in block_nums)
    request_json = f'[{request_data}]'.encode()
    response = 'n/a'
    while True:
        get_block, get_ops = None, None
        try:
            try:
                response = await client.post(url, data=request_json)
                response.raise_for_status()
            except Exception as e:
                logger.error('error fetching blocks, retrying once...', e=e)
                response = await client.post(url, data=request_json)
                response.raise_for_status()

            jsonrpc_response = await response.json()
            if not isinstance(jsonrpc_response, list):
                raise ValueError(f'Bad JSONRPC response: {jsonrpc_response}')

            response_pairs = funcy.partition(2, jsonrpc_response)
            results = []
            for get_block, get_ops in response_pairs:
                assert int(get_block['id']) == int(
                    get_ops['id']), f"{get_block['id']} != f{int(get_ops['id'])}"
                results.append((get_block['id'], get_block['result'], get_ops['result']))
            assert len(results) == len(
                block_nums), f'response list length ({len(results)}) != length of block_nums ({len(block_nums)})'
            return results
        except Exception as e:
            logger.exception('error fetching ops in block',
                             e=e, response=response, block=get_block, ops=get_ops)


async def store_block_and_ops(pool, prepared_block, prepared_ops):
    """Atomic add block,operations, and virtual operations in block



    :param pool:
    :param prepared_block:
    :param prepared_ops:
    :return:
    """

    raw_add_account_stmt = STATEMENT_CACHE['account']
    raw_stmts = [(STATEMENT_CACHE['block'], prepared_block.values())]

    for prepared_op in prepared_ops:
        raw_stmts.append((get_op_insert_stmt(prepared_op), prepared_op.values()))

    async with pool.acquire() as conn:
        prepared_stmts = [await conn.prepare(stmt) for stmt, _ in raw_stmts]
        stmts = zip(prepared_stmts, (vals for _, vals in raw_stmts))

        try:
            async with conn.transaction():
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
                                         prepared=prepared,
                                         stmt=stmt,
                                         type=prepared.get('operation_type'))
                        raise e
        except (asyncpg.exceptions.ForeignKeyViolationError) as e:
            async with conn.transaction():
                # collect all account names referenced in block and ops
                account_name_records = [(a,) for a in prepared_block['accounts']]
                await conn.executemany(raw_add_account_stmt, account_name_records)
                for i, stmt in enumerate(stmts):
                    query, args = stmt
                    try:
                        await query.fetchval(*args)
                        return
                    except Exception as e:
                        logger.exception('second error while storing block and ops',
                                         e=e, stmt=stmt, prepared_block=prepared_block)
                        raise e


async def process_block(block_num, raw_block, raw_ops, pool, loop=None):
    if raw_ops:
        prepared_futures = [prepare_raw_operation_for_storage(raw_op, loop=loop)
                            for raw_op in raw_ops]
        prepared_ops = await asyncio.gather(*prepared_futures)
    else:
        prepared_ops = []
    prepared_block = await prepare_raw_block_for_storage(raw_block, prepared_ops=prepared_ops, loop=loop)
    await store_block_and_ops(pool, prepared_block, prepared_ops)
    return (block_num, raw_block, prepared_block, raw_ops, prepared_ops)


# --- Operations ---
async def process_blocks(missing_block_nums, url, client, pool, _concurrency, jsonrpc_batch_size,
                         loop=None, results_queue=None):
    _logger = logger.bind(pid=os.getpid())
    block_num_batches = chunkify(missing_block_nums, jsonrpc_batch_size)
    _logger.debug('process_blocks', async_task_concurrency_limit=_concurrency,
                  jsonrpc_batch_size=jsonrpc_batch_size)

    fetch_coros = (fetch_blocks_and_ops_in_blocks(url, client, block_num_batch)
                   for block_num_batch in block_num_batches)

    to_fetch = set()
    window_size = 5000
    fetch_timings = deque(maxlen=window_size)
    store_timings = deque(maxlen=window_size)
    timings = dict()

    done = asyncio.queues.Queue(loop=loop)

    concurrency_low = _concurrency - 1
    concurrency_normal = _concurrency
    concurrency_high = _concurrency + 1
    concurrency = concurrency_normal

    def _add_fetch_task(fetch_coros=None, to_fetch=None, loop=None):
        coro = next(fetch_coros)
        f = asyncio.ensure_future(coro, loop=loop)
        timings[f] = {'fetch_start': time.perf_counter()}
        f.add_done_callback(on_fetch_completion)
        to_fetch.add(f)
    add_fetch_task = functools.partial(
        _add_fetch_task,
        fetch_coros=fetch_coros,
        to_fetch=to_fetch,
        loop=loop)

    def _on_fetch_completion(f, to_fetch=None, pool=None, done=None, loop=None):
        fetch_timings.append(time.perf_counter() - timings[f]['fetch_start'])
        to_fetch.remove(f)
        del timings[f]
        try:
            fetch_block_op_results = f.result()
        except Exception as e:
            logger.error('_on_fetch_completion', e=e)
            return
        for block_num, block, ops in fetch_block_op_results:
            f2 = asyncio.ensure_future(process_block(block_num, block, ops, pool, loop=loop))
            timings[f2] = {'store_start': time.perf_counter()}
            f2.add_done_callback(lambda f: done.put_nowait(f))

    on_fetch_completion = functools.partial(
        _on_fetch_completion,
        to_fetch=to_fetch,
        pool=pool,
        done=done,
        loop=loop)

    # schedule inital batch of coros
    while len(to_fetch) < concurrency:
        try:
            add_fetch_task()
        except StopIteration:
            return

    logger.debug('process_blocks scheduled initial batch of coros', concurrency=concurrency)

    loop_count = 0
    loop_start = time.perf_counter()
    block_rates = deque(maxlen=3)

    while True:
        loop_count += jsonrpc_batch_size
        f = await done.get()
        try:
            store_timings.append(time.perf_counter() - timings[f]['store_start'])
            del timings[f]
            result = f.result()

        except KeyboardInterrupt as e:
            raise e

        except Exception as e:
            logger.error('process_blocks result error', e=e, exc_info=True)
            raise e

        if loop_count % 500 == 0:
            results_queue.put_nowait(500)

            if loop_count >= window_size:

                loop_elapsed = time.perf_counter() - loop_start

                avg_batch_fetch_time = sum(fetch_timings) / window_size
                avg_block_ops_fetch_time = avg_batch_fetch_time / jsonrpc_batch_size
                avg_store_time = sum(store_timings) / window_size
                avg_block_time = avg_block_ops_fetch_time + avg_store_time
                block_rate = window_size / loop_elapsed
                block_rates.append(block_rate)
                avg_block_rate = sum(block_rates) / len(block_rates)

                if avg_store_time > 1:
                    concurrency = concurrency_low
                elif block_rate < avg_block_rate:
                    concurrency = concurrency_high

                logger.debug('loop',
                             concurrency=concurrency,
                             jsonrpc_batch_size=jsonrpc_batch_size,
                             done_size=done.qsize(),
                             to_fetch=len(to_fetch),
                             timing_window_size=window_size,
                             avg_batch_fetch_time=avg_batch_fetch_time,
                             avg_block_ops_fetch_time=avg_block_ops_fetch_time,
                             avg_store_time=avg_store_time,
                             avg_block_time=avg_block_time,
                             loop_elapsed=loop_elapsed,
                             block_rate=block_rate,
                             avg_block_rate=avg_block_rate
                             )

                loop_count = 0
                loop_start = time.perf_counter()

        while len(to_fetch) < concurrency:
            try:
                add_fetch_task()
            except StopIteration:
                return


def _process_pool_executor_target(missing_block_nums,
                                  database_url=None,
                                  steemd_http_url=None,
                                  concurrency=None,
                                  jsonrpc_batch_size=None,
                                  tcp_connection_limit=None,
                                  db_connection_limit=None,
                                  results_queue=None
                                  ):
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    _logger = logger.bind(pid=os.getpid())

    CONNECTOR = TCPConnector(loop=loop, limit=tcp_connection_limit)
    _logger.debug('creating aiohttp TCPConnector', tcp_connection_limit=tcp_connection_limit)
    aiohttp_session = aiohttp.ClientSession(loop=loop,
                                            connector=CONNECTOR,
                                            json_serialize=json.dumps,
                                            headers={
                                                'Content-Type': 'application/json'
                                            })

    pool = create_asyncpg_pool(database_url, max_size=db_connection_limit)
    try:
        loop.run_until_complete(process_blocks(missing_block_nums,
                                               steemd_http_url,
                                               aiohttp_session,
                                               pool,
                                               concurrency,
                                               jsonrpc_batch_size,
                                               loop=loop,
                                               results_queue=results_queue))
    except Exception as e:
        raise e
    finally:
        loop.run_until_complete(pool.close())
        loop.run_until_complete(aiohttp_session.close())
    return True


def task_add_missing_blocks(database_url=None,
                            steemd_http_url=None,
                            concurrency=None,
                            num_procs=None,
                            jsonrpc_batch_size=None,
                            missing_block_nums=None,
                            existing_count=None,
                            missing_count=None,
                            tcp_connection_limit=None,
                            db_connection_limit=None,
                            range_count=None):

    num_procs = num_procs or os.cpu_count()
    block_nums_chunks = split_into_num_chunks(missing_block_nums, num_procs)
    block_nums_per_proc = len(block_nums_chunks[0])

    tcp_connection_limit = concurrency + 10
    db_connection_limit = 10
    logger.info('initializing process pool',
                num_procs=num_procs,
                block_nums_per_proc=block_nums_per_proc,
                jsonrpc_batch_size=jsonrpc_batch_size,
                concurrency=concurrency,
                tcp_connection_limit=tcp_connection_limit,
                db_connection_limit=db_connection_limit)

    proc_func = functools.partial(_process_pool_executor_target,
                                  database_url=database_url,
                                  steemd_http_url=steemd_http_url,
                                  concurrency=concurrency,
                                  jsonrpc_batch_size=jsonrpc_batch_size,
                                  tcp_connection_limit=tcp_connection_limit,
                                  db_connection_limit=db_connection_limit,
                                  results_queue=RESULTS_Q)

    blocks_progress_bar = tqdm(initial=existing_count,
                               total=range_count,
                               bar_format='{bar}| [{rate_fmt}{postfix}]',
                               ncols=48,
                               dynamic_ncols=False,
                               unit=' blocks',
                               )

    with ProcessPoolExecutor(max_workers=num_procs) as proc_pool:
        results_future = proc_pool.map(proc_func, block_nums_chunks,
                                       chunksize=1)
        while True:
            result = RESULTS_Q.get(timeout=80)
            #logger.debug('result', result_len=len(result))
            blocks_progress_bar.update(result)
