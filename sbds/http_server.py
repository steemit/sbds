# -*- coding: utf-8 -*-

import click
from sqlalchemy import create_engine
import os
from bottle import route, run


from sbds.logging import getLogger
logger = getLogger(__name__)

from sbds.storages.db import Blocks
from sbds.storages.db import Transactions
from sbds.storages.db.tables import meta
from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db import extract_transaction_from_block
from sbds.utils import chunkify



database_url = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
engine = create_engine(database_url, execution_options={'stream_results': True})
blocks = Blocks(engine=engine)
transactions = Transactions(engine=engine)


@route('/')
def health():
    return dict(latest_block=len(blocks))




# Development server

@click.command()
def dev_server():
    run(host='localhost', port=8080, debug=True)