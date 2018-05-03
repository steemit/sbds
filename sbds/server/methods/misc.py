# -*- coding: utf-8 -*-
from sbds.storages.db.tables.operations import op_db_table_for_type


async def count_account_create_with_delegation_operations(context=None):
    """
    This function demonstrates how to write a method to run
    an SQL query which returns a single number

    :param context:
    :return: int
    """
    engine = context['aiohttp_request'].app['db']
    query = 'SELECT COUNT(*) FROM sbds_op_account_create_with_delegations'
    async with engine.acquire() as conn:
        return await conn.scalar(query)


async def recent_account_create_with_delegation_operations(context=None):
    """
    This function demonstrates how to write a method to run
    an SQL query which returns rows

    :param context:
    :return: List[Dict]

    """
    engine = context['aiohttp_request'].app['db']
    query = 'SELECT * FROM sbds_op_account_create_with_delegations ORDERBY timestamp DESC LIMIT 5'
    async with engine.acquire() as conn:
        cursor = await conn.execute(query)
        return await cursor.fetchall()
