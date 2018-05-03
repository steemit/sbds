# -*- coding: utf-8 -*-
import structlog

from sbds.storages.db.tables import Base
from sbds.storages.db.tables import init_tables

import sbds.sbds_logging

# pylint: skip-file
logger = structlog.get_logger(__name__)


def task_init_db_if_required(database_url):
    init_tables(database_url, Base.metadata)
