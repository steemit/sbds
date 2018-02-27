# -*- coding: utf-8 -*-
import asyncio
import datetime
import functools
import json
import os

import structlog
import uvloop

from aiohttp import web
from aiopg import sa
from jsonrpcserver import config
from jsonrpcserver.async_methods import AsyncMethods


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


async def handle_api(request):
    request = await request.json()
    context = {'request': request}
    response = await api_methods.dispatch(request, context=context)
    return json_response(response)


# pylint: disable=unused-argument
async def start_background_tasks(app):
    logger.info('starting tasks')


# pylint: enable=unused-argument


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


# pylint: disable=unused-argument
async def healthcheck_handler(request):
    return web.json_response(await api_healthcheck(request))


async def on_cleanup(app):
    logger.info('executing on_cleanup signal handler')


# pylint: enable=unused-argument

app = web.Application()
api_methods = AsyncMethods()
app.router.add_post('/', handle_api)
app.router.add_get('/.well-known/healthcheck.json', healthcheck_handler)
app.router.add_get('/health', healthcheck_handler)
api_methods.add(api_healthcheck, 'sbds.health')


def run(host=None, port=None):
    app = web.Application()
    api_methods = AsyncMethods()
    app.router.add_post('/', handle_api)
    app.router.add_get('/.well-known/healthcheck.json', healthcheck_handler)
    app.router.add_get('/health', healthcheck_handler)

    api_methods.add(api_healthcheck, 'sbds.health')
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(on_cleanup)
    web.run_app(app, host=host, port=port)
