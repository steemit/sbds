# -*- coding: utf-8 -*-
import asyncio
import datetime
import functools
import json
import os

import aiohttp
import aiopg.sa
import asyncpg
import structlog
import uvloop

from aiohttp import web


from aiohttp.connector import TCPConnector
from jsonrpcserver import config
from jsonrpcserver.async_methods import AsyncMethods


from .handlers import handle_api
from .handlers import handle_healthcheck


from .methods import get_account_history

import sbds.sbds_logging

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
    pool = await asyncpg.create_pool(database_url,
                                     min_size=10,
                                     max_size=20,
                                     **database_extra)
    app['db'] = pool
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
        http_client_max_tcp_conn,
        http_client_timeout,
        database_url,
        steemd_http_url,
        **kwargs):

    app_extra = kwargs.get('app_extra', {})

    # layout basic aiohttp config and context
    app = web.Application()
    app['config'] = dict(
        http_client_max_tcp_conn=http_client_max_tcp_conn,
        http_client_timeout=http_client_timeout,
        database_url=database_url,
        steemd_http_url=steemd_http_url
    )
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
    jsonrpc_methods.add(get_account_history)

    # add jsonrpc method dispatcher to aiohttp app context
    app['jsonrpc_methods_dispatcher'] = jsonrpc_methods

    # run aiohttp webapp
    web.run_app(app, host=http_host, port=http_port)
