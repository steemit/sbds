# -*- coding: utf-8 -*-
from datetime import datetime
import os

import click
from sqlalchemy import create_engine

from bottle import route, run
from sbds.http_client import SimpleSteemAPIClient

from sbds.logging import getLogger


from sbds.storages.db import Blocks
from sbds.storages.db import Transactions
from sbds.storages.db.tables import meta
from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db import extract_transaction_from_block
from sbds.utils import chunkify


logger = getLogger(__name__)

rpc = SimpleSteemAPIClient()

database_url = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
engine = create_engine(database_url, execution_options={'stream_results': True})
blocks = Blocks(engine=engine)
transactions = Transactions(engine=engine)


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