# -*- coding: utf-8 -*-
from datetime import datetime
import os

import click
from sqlalchemy import create_engine

from bottle import route, run
from sbds.http_client import SimpleSteemAPIClient
import maya

from sbds.logging import getLogger


from sbds.storages.db import Blocks
from sbds.storages.db import Transactions
from sbds.storages.db.tables import meta
from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db import extract_transactions_from_block
from sbds.utils import chunkify


logger = getLogger(__name__)


url = os.environ.get('STEEMD_HTTP_URL')
rpc = SimpleSteemAPIClient(url=url)
database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url, execution_options={'stream_results': True})
blocks = Blocks(engine=engine)
transactions = Transactions(engine=engine)


def past_24_hours():
    return maya.now().iso8601(), maya.when('yesterday').iso8601()

def past_48_hours():
    return maya.now().iso8601(), maya.when('day before yesterday').iso8601()

def past_72_hours():
    return maya.now().iso8601(), maya.when('72 hours ago').iso8601()

'''



'''



@route('/health')
def health():
    last_db_block = len(blocks)
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    return dict(last_db_block=last_db_block,
                last_irreversible_block=last_irreversible_block,
                diff=diff,
                timestamp=datetime.utcnow().isoformat())





# Development server

@click.command()
def dev_server():
    run(host='localhost', port=8080, debug=True)