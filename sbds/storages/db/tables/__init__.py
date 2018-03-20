# -*- coding: utf-8 -*-
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ENUM





metadata = MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker()

# pylint: disable=wrong-import-position
from ..utils import isolated_nullpool_engine


def init_tables(database_url, _metadata, checkfirst=True):
    """Create any missing tables on the database"""
    import sbds.storages.db.tables.operations
    import sbds.storages.db.tables.block
    import sbds.storages.db.tables.meta
    with isolated_nullpool_engine(database_url) as engine:
        _metadata.create_all(bind=engine, checkfirst=checkfirst)


def reset_tables(database_url, _metadata):
    """Drop and then create tables on the database"""

    # use reflected MetaData to avoid errors due to ORM classes
    # being inconsistent with existing tables
    with isolated_nullpool_engine(database_url) as engine:
        seperate_metadata = MetaData()
        seperate_metadata.reflect(bind=engine)
        seperate_metadata.drop_all(bind=engine)
        ENUM(name='sbds_operation_types').drop(engine)

    # use ORM clases to define tables to create
    init_tables(database_url, _metadata)


def test_connection(database_url):
    _metadata = MetaData()
    with isolated_nullpool_engine(database_url) as engine:
        try:
            _metadata.reflect(bind=engine)
            table_count = len(_metadata.tables)
            url = engine.url
            return url, table_count
        except Exception as e:
            return False, e


def get_table_count(database_url):
    return len(get_tables(database_url))


def get_tables(database_url):
    with isolated_nullpool_engine(database_url) as engine:
        tables = engine.table_names()
    return tables
