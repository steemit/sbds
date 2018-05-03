# -*- coding: utf-8 -*-

import structlog

from sbds.storages.db.tables import test_connection

# pylint: skip-file
logger = structlog.get_logger(__name__)


def task_confirm_db_connectivity(database_url):
    url, table_count = test_connection(database_url)
    if not url:
        raise Exception('Unable to connect to database')

    return f'connected to {url.__repr__()} and found {table_count} tables'
