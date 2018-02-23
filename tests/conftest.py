# -*- coding: utf-8 -*-


import pytest
import requests
from requests.exceptions import ConnectionError

from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db.tables import Session
from sbds.storages.db.utils import configure_engine

import sbds
import sbds.chain
import sbds.chain.cli
import sbds.server
import sbds.server.cli
import sbds.server.methods
import sbds.server.serve
import sbds.storages
import sbds.storages.db
import sbds.storages.db.cli
import sbds.storages.db.data_types
import sbds.storages.db.enums
import sbds.storages.db.field_handlers
import sbds.storages.db.query_helpers
import sbds.storages.db.utils
import sbds.storages.db.scripts
import sbds.storages.db.scripts.populate
import sbds.storages.db.tables.async_core
import sbds.storages.db.tables.block
import sbds.storages.db.tables.core
import sbds.storages.db.tables.operations



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
        timeout=60.0, pause=0.1, check=lambda: is_responsive(url))
    return url
