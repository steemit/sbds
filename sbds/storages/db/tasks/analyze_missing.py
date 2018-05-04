# -*- coding: utf-8 -*-
import asyncio

import asyncpg
import requests
import structlog
import uvloop

# pylint: skip-file
logger = structlog.get_logger(__name__)


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


async def get_existing_and_missing_count(pool, start_block, end_block):
    async with pool.acquire() as conn:
        existing_count = await conn.fetchval('SELECT COUNT(timestamp) from sbds_core_blocks WHERE block_num >=$1 AND block_num <= $2', start_block, end_block)
    range_count = len(range(start_block, end_block + 1))
    missing_count = range_count - existing_count
    logger.info(f'get_existing_and_missing_count',
                existing_count=existing_count,
                missing_count=missing_count,
                range_count=range_count)
    return existing_count, missing_count, range_count


async def get_last_irreversible_block_num(steemd_http_url):
    response = requests.post(
        steemd_http_url,
        data=f'{{"id":1,"jsonrpc":"2.0","method":"get_dynamic_global_properties"}}'.encode())
    response.raise_for_status()
    jsonrpc_response = response.json()
    libn = jsonrpc_response['result']['last_irreversible_block_num']
    logger.info(f'get_last_irreversible_block_num', last_irreversible_block_num=libn)
    return libn


async def collect_missing_block_nums(pool, end_block, missing_count, start_block=None):
    start_block = start_block or 1
    complete_block_nums = range(start_block, end_block + 1)
    logger.debug('collect_missing_block_nums', end_block=end_block,
                 start_block=start_block)
    if missing_count == end_block:
        return list(complete_block_nums)

    query = '''
    SELECT generate_series($1::int,$2::int)
    EXCEPT
    SELECT block_num from sbds_core_blocks where block_num BETWEEN $3 AND $4;
    '''

    async with pool.acquire() as conn:
        records = await conn.fetch(query, start_block, end_block, start_block, end_block)

    return [r[0] for r in records]


async def async_task_collect_missing_block_nums(database_url=None, steemd_http_url=None, start_block=None, end_block=None):
    async with asyncpg.create_pool(database_url) as pool:
        start_block = start_block or 1
        if end_block is None or end_block <= 0:
            end_block = await get_last_irreversible_block_num(steemd_http_url)
            logger.info(f'last irreversible block number: {end_block}')
        existing_count, missing_count, range_count = await get_existing_and_missing_count(pool, start_block, end_block)
        missing_block_nums = await collect_missing_block_nums(pool, end_block, missing_count, start_block=start_block)

    return dict(missing_block_nums=missing_block_nums,
                existing_count=existing_count,
                missing_count=missing_count,
                range_count=range_count)


def task_collect_missing_block_nums(
        database_url=None, steemd_http_url=None, start_block=None, end_block=None):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        async_task_collect_missing_block_nums(database_url=database_url,
                                              steemd_http_url=steemd_http_url,
                                              start_block=start_block,
                                              end_block=end_block)
    )
