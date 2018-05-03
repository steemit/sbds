# -*- coding: utf-8 -*-
import asyncio

from collections import namedtuple
from contextlib import contextmanager

import structlog
import uvloop

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import NullPool


logger = structlog.get_logger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


EngineConfig = namedtuple('EngineConfig',
                          ['database_url', 'url', 'engine_kwargs', 'engine'])


def configure_engine(database_url, **kwargs):
    if kwargs:
        base_engine_kwargs = kwargs
    else:
        base_engine_kwargs = dict()

    url = make_url(database_url)
    logger.debug('configuring engine', url=url.__repr__())
    backend = url.get_backend_name()

    if backend == 'sqlite':
        logger.debug('configuring sqlite backend')
        engine_kwargs = base_engine_kwargs
    if backend == 'mysql':
        logger.debug('configuring mysql backend')
        if 'charset' not in url.query:
            logger.debug('adding `charset=utf8mb4` to mysql engine config')
            url.query.update(charset='utf8mb4')

        engine_kwargs = base_engine_kwargs
        engine_kwargs.update(server_side_cursors=True, encoding='utf8')
    else:
        logger.debug('configuring backend', backend=backend)
        engine_kwargs = base_engine_kwargs
    logger.debug('engine_kwargs', **engine_kwargs)

    engine = create_engine(url, **engine_kwargs)

    # create tables for in-memory db
    if backend == 'sqlite' and url.database is None:
        from .tables import Base
        Base.metadata.create_all(bind=engine, checkfirst=True)

    return EngineConfig(database_url, url, engine_kwargs, engine)


def configure_nullpool_engine(database_url, poolclass=NullPool, **kwargs):
    if kwargs:
        kwargs.pop('poolclass', None)
    return configure_engine(database_url, poolclass=poolclass, **kwargs)


@contextmanager
def isolated_nullpool_engine(database_url, **kwargs):
    engine_config = configure_nullpool_engine(database_url, **kwargs)
    engine = engine_config.engine
    try:
        yield engine
    except Exception as e:
        logger.info('error', e=e)
    finally:
        del engine_config
        engine.dispose()
        del engine


@contextmanager
def isolated_engine(database_url, **kwargs):
    engine_config = configure_engine(database_url, **kwargs)
    engine = engine_config.engine
    try:
        yield engine
    except Exception as e:
        logger.info('error', e=e)
    finally:
        del engine_config
        engine.dispose()
        del engine


@contextmanager
def isolated_engine_config(database_url, **kwargs):
    engine_config = configure_engine(database_url, **kwargs)
    try:
        yield engine_config
    except Exception as e:
        logger.info(e)
    finally:
        engine_config.engine.dispose()
        del engine_config
