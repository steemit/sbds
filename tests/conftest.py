# -*- coding: utf-8 -*-
import pytest
import tempfile

import sbds
import sbds.http_client

import sbds.sbds_logging
import sbds.sbds_json
import sbds.utils

import sbds.chain

import sbds.checkpoints

import sbds.server
import sbds.server.utils
import sbds.server.input_parsers

import sbds.storages
import sbds.storages.db
import sbds.storages.db.cli
import sbds.storages.db.enums
import sbds.storages.db.field_handlers
import sbds.storages.db.query_helpers
import sbds.storages.db.utils
import sbds.storages.db.tables
import sbds.storages.db.tables.core
import sbds.storages.db.tables.tx

import sbds.storages.s3
import sbds.storages.s3.cli

from sbds.http_client import SimpleSteemAPIClient

from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session
from sbds.storages.db.tables import init_tables
from sbds.storages.db.utils import configure_engine


# pylint: skip-file
@pytest.fixture()
def sqlitedb_session(sqlite_db_url=None):
    sqlite_db_url = sqlite_db_url or 'sqlite://'
    engine_config = configure_engine(sqlite_db_url)
    session = Session(bind=engine_config.engine)
    return session


@pytest.fixture()
def sqlitedb_engine_config(sqlite_db_url=None):
    sqlite_db_url = sqlite_db_url or 'sqlite://'
    sqlite_engine_config = configure_engine(sqlite_db_url)


@pytest.fixture()
def sqlitedb_tmpfile_db_url():
    fh, tmp_db_path = tempfile.mkstemp()
    sqlite_db_url = 'sqlite:///%s' % tmp_db_path
    return sqlite_db_url


@pytest.fixture()
def blocks_without_txs(http_client, number_of_blocks=5):
    return list(map(http_client.get_block, range(1, 1 + number_of_blocks)))


@pytest.fixture()
def blocks_with_txs(http_client, number_of_blocks=5):
    return list(
        map(http_client.get_block, range(1092, 1092 + number_of_blocks)))


@pytest.fixture()
def first_block_dict():
    return {
        'extensions': [],
        'previous':
        '0000000000000000000000000000000000000000',
        'timestamp':
        '2016-03-24T16:05:00',
        'transaction_merkle_root':
        '0000000000000000000000000000000000000000',
        'transactions': [],
        'witness':
        'initminer',
        'witness_signature':
        '204f8ad56a8f5cf722a02b035a61b500aa59b9519b2c33c77a80c0a714680a5a5a7a340d909d19996613c5e4ae92146b9add8a7a663eef37d837ef881477313043'
    }


@pytest.fixture()
def http_client(url='https://steemd.steemitdev.com', **kwargs):
    return SimpleSteemAPIClient(url, **kwargs)
