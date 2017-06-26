# -*- coding: utf-8 -*-
import pytest
import tempfile
import requests
import json
import os

from requests.exceptions import ConnectionError


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

OPERATION_SCHEMA_FILENAME = 'operations.json'
OPERATIONS_SCHEMA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                      OPERATION_SCHEMA_FILENAME)

with open(OPERATIONS_SCHEMA_PATH) as f:
    orig_operations_schema = json.load(f)
    _operations_schema = dict()
    for k,v in orig_operations_schema.items():
        name = k.replace('_operation','')
        _operations_schema[name] = v

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
      "previous": "0000000000000000000000000000000000000000",
      "timestamp": "2016-03-24T16:05:00",
      "witness": "initminer",
      "transaction_merkle_root": "0000000000000000000000000000000000000000",
      "extensions": [],
      "witness_signature": "204f8ad56a8f5cf722a02b035a61b500aa59b9519b2c33c77a80c0a714680a5a5a7a340d909d19996613c5e4ae92146b9add8a7a663eef37d837ef881477313043",
      "transactions": [],
      "block_id": "0000000109833ce528d5bbfb3f6225b39ee10086",
      "signing_key": "STM8GC13uCZbP44HzMLV6zPZGwVQ8Nt4Kji8PapsPiNq1BK153XTX",
      "transaction_ids": []
    }


@pytest.fixture()
def http_client(url='https://steemd.steemitdev.com', **kwargs):
    return SimpleSteemAPIClient(url, **kwargs)


def is_responsive(url):
    """Check if something responds to ``url``."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False

@pytest.fixture(scope='session')
def sbds_http_server(docker_ip, docker_services):
    """Ensure that "some service" is up and responsive."""
    url = 'http://localhost:9191'
    docker_services.wait_until_responsive(
       timeout=60.0, pause=0.1,
       check=lambda: is_responsive(url)
    )
    return url

@pytest.fixture(scope='session',
                params=_operations_schema.items(),
                ids=list(_operations_schema.keys()))
def operation_schema(request):
    return request.param