# -*- coding: utf-8 -*-

import structlog

from sbds.storages.db.utils import isolated_engine

# pylint: skip-file
logger = structlog.get_logger(__name__)


def task_load_db_meta(database_url):
    with isolated_engine(database_url) as engine:
        from sqlalchemy import MetaData
        m = MetaData()
        m.reflect(bind=engine)
    return m
