# -*- coding: utf-8 -*-
import asyncio

import asyncpg
import rapidjson
import structlog
import uvloop

# pylint: skip-file
logger = structlog.get_logger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


async def async_task_load_account_names(database_url=None, accounts_file=None):
    with open(accounts_file) as f:
        account_names = rapidjson.load(f)
    async with asyncpg.create_pool(database_url) as pool:
        non_blank_account_names = (a for a in account_names if a is not None)
        unique_account_names = set(non_blank_account_names)
        account_name_records = [(i, a) for i, a in enumerate(unique_account_names, 1)]
        async with pool.acquire() as conn:
            try:
                await conn.copy_records_to_table('sbds_meta_accounts', records=account_name_records)
            except Exception as e:
                logger.exception('error preloading account names', e=e)
        del account_names


def task_load_account_names(database_url=None, accounts_file=None, loop=None):
    loop = loop or asyncio.get_event_loop()
    return loop.run_until_complete(
        async_task_load_account_names(database_url=database_url,
                                      accounts_file=accounts_file))
