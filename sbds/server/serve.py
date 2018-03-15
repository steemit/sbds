# -*- coding: utf-8 -*-
import asyncio
import datetime
import functools
import json
import os

import aiopg.sa
import structlog
import uvloop

from aiohttp import web

from jsonrpcserver import config
from jsonrpcserver.async_methods import AsyncMethods
from sqlalchemy.engine.url import make_url

from .methods.account_history_api.methods import get_ops_in_block
from .methods.account_history_api.methods import get_account_history

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

config.log_responses = False
config.log_requests = False

logger = structlog.get_logger(__name__)

# pylint: disable=redefined-outer-name


def default_json(obj):
    if isinstance(obj, datetime.datetime):
        return str(obj)
    raise TypeError('Unable to serialize {!r}'.format(obj))


json_dumps = functools.partial(json.dumps, default=default_json)
json_response = functools.partial(web.json_response, dumps=json_dumps)


async def init_pg(app):
    database_url = app['config']['database_url']
    database_extra = app['config'].get('database_extra', {})
    parsed_db_url = make_url(database_url)
    database_kwargs = dict(
        database=parsed_db_url['database'],
        user=parsed_db_url['user'],
        password=parsed_db_url['password'],
        host=parsed_db_url['host'],
        port=parsed_db_url['port'],
        **database_extra
    )
    engine = await aiopg.sa.create_engine(**database_kwargs, loop=app.loop)
    app['db'] = engine


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


async def api_healthcheck(request):
    db = request.config.db
    block_cls = request.config.Block
    rpc = request.config.rpc
    app = request.app
    last_db_block = block_cls.highest_block(db)
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    if diff > app.config['sbds.MAX_BLOCK_NUM_DIFF']:
        return json_response(
            500,
            'last irreversible block (%s) - highest db block (%s) = %s, > max allowable difference (%s)'
            % (last_irreversible_block, last_db_block, diff,
               app.config['sbds.MAX_BLOCK_NUM_DIFF']))

    return {
        'status': 'OK',
        'source_commit': os.environ.get('SOURCE_COMMIT'),
        'docker_tag': os.environ.get('DOCKER_TAG'),
        'datetime': datetime.datetime.utcnow().isoformat(),
        'last_db_block': last_db_block,
        'last_irreversible_block': last_irreversible_block,
        'diff': diff
    }


async def healthcheck_handler(request):
    return web.json_response(await api_healthcheck(request))


async def on_cleanup(app):
    logger.info('executing on_cleanup signal handler')


def run(host=None,
        port=None,
        database_url=None,
        database_extra=None,
        app_extra=None,
        **kwargs):
    app_extra = app_extra or dict()

    # layout basic aiohttp config and context
    app = web.Application()
    app['config'] = dict()
    if kwargs:
        app['config'].update(**kwargs)
    app['config']['database_url'] = database_url
    app['config']['database_extra'] = database_extra
    app['db'] = None  # this will be defined by init_pg at app startup

    # register app lifecycle callbacks
    app.on_startup.append(init_pg)
    app.on_cleanup.append(on_cleanup)

    # register app routes
    app.router.add_post('/', handle_api)
    app.router.add_get('/.well-known/healthcheck.json', healthcheck_handler)
    app.router.add_get('/health', healthcheck_handler)

    # create jsonrpc method dispatcher
    jsonrpc_methods = AsyncMethods()

    # register jsonrpc methods with dispatcher
    jsonrpc_methods.add(api_healthcheck, 'sbds.health')
    # TODO add additional methods here

    # add jsonrpc method dispatcher to aiohttp app context
    app['jsonrpc_methods_dispatcher'] = jsonrpc_methods

    # run aiohttp webapp
    web.run_app(app, host=host, port=port, **app_extra)
