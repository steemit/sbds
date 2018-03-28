# -*- coding: utf-8 -*-
import asyncio

import async_timeout

from sbds.sbds_json import loads
from sbds.sbds_json import dumps


async def get_dynamic_global_properties(session, url, timeout):
    data = b'{"id":1,"jsonrpc":"2.0","method":"database_api.get_dynamic_global_properties"}'
    async with async_timeout.timeout(timeout):
        async with session.post(url, data=data) as response:
            return await response.json()['result']


async def get_trending_tags(session, url, timeout):
    data = b'{"id":1,"jsonrpc":"2.0","method":"tags_api.get_trending_tags"}'
    async with async_timeout.timeout(timeout):
        async with session.post(url, data=data) as response:
            return await response.json()['result']


async def get_witness_schedule(session, url, timeout):
    data = b'{"id":1,"jsonrpc":"2.0","method":"database_api.get_witness_schedule"}'
    async with async_timeout.timeout(timeout):
        async with session.post(url, data=data) as response:
            return await response.json()['result']


async def get_current_median_history_price(session, url, timeout):
    data = b'{"id":1,"jsonrpc":"2.0","method":"condenser_api.get_current_median_history_price","params":[]}'
    async with async_timeout.timeout(timeout):
        async with session.post(url, data=data) as response:
            return await response.json()['result']


async def handle_get_state_hot(path):
    return 'HOT'


async def get_path_handlers(path):
    parts = path.split('/')
    if parts[0] == 'hot':
        return {'content': handle_get_state_hot(path)}
    return {}


async def get_state(path, context=None):
    """
    This function demonstrates how to write a method to run
    an SQL query which returns a single number

    :param context:
    :return: int
    """
    engine = context['aiohttp_request'].app['db']
    session = context['aiohttp_request'].app['http']['session']
    url = context['aiohttp_request'].app['http']['url']
    timeout = context['aiohttp_request'].app['http']['timeout']

    query = 'FIXME'

    handlers = {
        'props': get_dynamic_global_properties(session, url, timeout),
        'tags': get_trending_tags(session, url, timeout),
        'witness_schedule': get_witness_schedule(session, url, timeout),
        'feed_price': get_current_median_history_price(session, url, timeout),
        # probably add additional function calls here
        **get_path_handlers(path)
    }

    try:
        result_values = await asyncio.gather(*list(handlers.values()))
        results = dict(zip(handlers.keys(), result_values))

        return {
            "current_route": path,
            "props": results['props'],
            "tag_idx": {
                "trending": results['tags']
            },
            "tags": {},
            "content": {},
            "accounts": {},
            "witnesses": {},
            "discussion_idx": {},
            "witness_schedule": results['witness_schedule'],
            "feed_price": results['feed_price'],
            "error": ""
        }
    except BaseException:
        return 'error'  # FIXME
