# -*- coding: utf-8 -*-
import asyncio
import datetime
import functools
import json
import os

import aiohttp
import aiopg.sa
import structlog
import uvloop

from aiohttp import web


from aiohttp.connector import TCPConnector
from jsonrpcserver import config
from jsonrpcserver.async_methods import AsyncMethods
from sqlalchemy.engine.url import make_url

from .handlers import handle_api
from .handlers import handle_healthcheck

from .methods.account_history_api import get_ops_in_block
from .methods.account_history_api import get_account_history
from .methods.account_history import get_state

from sbds.sbds_json import loads
from sbds.sbds_json import dumps

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

MAX_CLIENT_TCP_CONNECTIONS = 100

config.log_responses = False
config.log_requests = False

logger = structlog.get_logger(__name__)

# pylint: disable=redefined-outer-name


json_response = functools.partial(web.json_response, dumps=dumps)


async def pg(app):
    database_url = app['config']['database_url']
    database_extra = app['config'].get('database_extra', {})
    parsed_db_url = make_url(database_url)
    database_kwargs = dict(
        database=parsed_db_url.database,
        user=parsed_db_url.username,
        password=parsed_db_url.password,
        host=parsed_db_url.host,
        port=parsed_db_url.port,
        **database_extra
    )
    engine = await aiopg.sa.create_engine(**database_kwargs, loop=app.loop)
    app['db'] = engine
    yield
    await app['db'].close()


async def http_client(app):
    connector = TCPConnector(loop=app.loop,
                             limit=app['config']['http_client_max_tcp_conn'])
    session = aiohttp.ClientSession(
        skip_auto_headers=['User-Agent'],
        loop=app.loop,
        connector=connector,
        json_serialize=dumps,
        headers={'Content-Type': 'application/json'})
    app['http'] = {
        'session': session,
        'url': app['config']['steemd_http_url'],
        'timeout': app['config']['http_client_timeout']
    }

    yield
    await app['http']['session'].close()


def run(http_host,
        http_port,
        **kwargs):

    app_extra = kwargs.get('app_extra', {})

    # layout basic aiohttp config and context
    app = web.Application()
    app['config'] = dict()
    if kwargs:
        app['config'].update(**kwargs)

    app['db'] = None  # defined by pg at startup
    app['http'] = None  # defined by http_client at startup

    # register app lifecycle callbacks
    app.cleanup_ctx.append(pg)
    app.cleanup_ctx.append(http_client)

    # register app routes
    app.router.add_post('/', handle_api)
    app.router.add_get('/.well-known/healthcheck.json', handle_healthcheck)
    app.router.add_get('/health', handle_healthcheck)

    # create jsonrpc method dispatcher
    jsonrpc_methods = AsyncMethods()

    # register jsonrpc methods with dispatcher
    # TODO add additional methods here
    jsonrpc_methods.add(get_ops_in_block)
    jsonrpc_methods.add(get_state)
    jsonrpc_methods.add(get_account_history)

    # add jsonrpc method dispatcher to aiohttp app context
    app['jsonrpc_methods_dispatcher'] = jsonrpc_methods

    # run aiohttp webapp
    web.run_app(app, host=http_host, port=http_port)
