# -*- coding: utf-8 -*-
import async_timeout


async def fetch(session, url, timeout, **kwargs):
    async with async_timeout.timeout(timeout):
        async with session.post(url, **kwargs) as response:
            return await response.json()


async def db_scalar(engine, query, **kwargs):
    async with engine.acquire() as conn:
        return await conn.scalar(query)


async def get_dynamic_global_properties(session, url, timeout):
    data = b'{"id":1,"jsonrpc":"2.0","method":"database_api.get_dynamic_global_properties"}'
    async with async_timeout.timeout(timeout):
        async with session.post(url, data=data) as response:
            data = await response.json()
            return data['result']


async def get_last_irreversible_block_num(session, url, timeout):
    data = b'{"id":1,"jsonrpc":"2.0","method":"database_api.get_dynamic_global_properties"}'
    async with async_timeout.timeout(timeout):
        async with session.post(url, data=data) as response:
            data = await response.json()
            return data['result']['last_irreversible_block_num']


async def get_highest_db_block(engine):
    query = 'SELECT MAX(block_num) FROM sbds_core_blocks'
    return await db_scalar(engine, query)
