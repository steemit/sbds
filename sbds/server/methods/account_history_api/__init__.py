# -*- coding: utf-8 -*-

import sbds.sbds_json


async def get_account_history(account_name, context=None):
    """
    This function demonstrates how to write a method to run
    an SQL query which returns rows

    :param context:
    :return: List[Dict]

    """
    logger = context['logger']
    engine = context['aiohttp_request'].app['db']
    query = '''SELECT block_num, transaction_num, operation_num,operation_type, raw  from sbds_all_ops_view  where sbds_all_ops_view.accounts @> $1::jsonb LIMIT 100;'''
    async with engine.acquire() as conn:
        await conn.set_type_codec(
            'jsonb',
            encoder=sbds.sbds_json.dumps,
            decoder=sbds.sbds_json.loads,
            schema='pg_catalog'
        )
        async with conn.transaction():

            results = []
            logger.info('executing query', query=query,
                        account_name=account_name)
            async for record in conn.cursor(query, account_name):
                result = dict(record.items())
                results.append(result)
    return results
