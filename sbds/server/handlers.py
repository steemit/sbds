# -*- coding: utf-8 -*-
import asyncio
import datetime
import functools
import os


import structlog


from aiohttp import web

from .utils import get_last_irreversible_block_num
from .utils import get_highest_db_block

from sbds.sbds_json import dumps


logger = structlog.get_logger(__name__)

# pylint: disable=redefined-outer-name


json_response = functools.partial(web.json_response, dumps=dumps)


async def handle_api(aiohttp_request):
    """
    Dispatches aiohttp request to jsonrpcserver method, passing aiohttp request
    object as `context['aiohttp_request']` to jsonrcpserver method

    :param aiohttp_request:
    :return:
    """
    json_request_dict = await aiohttp_request.json()
    jsonrpc_request_context = {'aiohttp_request': aiohttp_request}
    jsonrpc_methods = aiohttp_request.app['jsonrpc_methods_dispatcher']
    jsonrpc_method_response = await jsonrpc_methods.dispatch(json_request_dict, context=jsonrpc_request_context)
    return json_response(jsonrpc_method_response)


async def handle_healthcheck(request):
    db = request.app['db']
    session = request.app['http']['session']
    url = request.app['http']['url']
    timeout = request.app['http']['timeout']

    app = request.app
    last_db_block = None
    last_irreversible_block = None
    diff = None

    try:
        last_db_block, last_irreversible_block = await asyncio.gather(
            get_highest_db_block(db),
            get_last_irreversible_block_num(session, url, timeout)
        )
        diff = last_irreversible_block - last_db_block
        max_diff = app['config'].get('sbds.MAX_BLOCK_NUM_DIFF', 10)
        if diff > max_diff:
            return json_response(
                status=500,
                text=f'last irreversible block_num {last_irreversible_block} - highest db block {last_db_block} = {diff}, > max allowable difference {max_diff}')

    except Exception as e:
        logger.exception('failed to calulate block diff', e=e, diff=diff,
                         last_irreversible_block=last_irreversible_block,
                         last_db_block=last_db_block)
        return json_response(status=500, text='error')

    status = {
        'status': 'OK',
        'source_commit': os.environ.get('SOURCE_COMMIT'),
        'docker_tag': os.environ.get('DOCKER_TAG'),
        'datetime': datetime.datetime.utcnow().isoformat(),
        'last_db_block': last_db_block,
        'last_irreversible_block': last_irreversible_block,
        'diff': diff
    }

    return json_response(status)
