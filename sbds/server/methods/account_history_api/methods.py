# -*- coding: utf-8 -*-
from sbds.storages.db.tables.operations import op_db_table_for_type


async def get_ops_in_block(block_num, only_virtual, context=None):
    """
    This function demonstrates how to write a method to run
    an SQL query which returns a single number

    :param context:
    :return: int
    """
    engine = context['aiohttp_request'].app['db']
    query = 'FIXME'
    async with engine.acquire() as conn:
        # FIXME
        return await conn.scalar(query)


async def get_account_history(account_name, context=None):
    """
    This function demonstrates how to write a method to run
    an SQL query which returns rows

    :param context:
    :return: List[Dict]

    """
    engine = context['aiohttp_request'].app['db']
    query = 'FIXME'
    async with engine.acquire() as conn:
        # FIXME
        cursor = await conn.execute(query)
        return await cursor.fetchall()
