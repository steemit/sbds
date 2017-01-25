# -*- coding: utf-8 -*-
from datetime import datetime
import os

import click
from sqlalchemy import create_engine

import bottle
from bottle import route, run, request, response


from sbds.http_client import SimpleSteemAPIClient
import maya

from sbds.logging import getLogger




from sbds.http_client import SimpleSteemAPIClient

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from sbds.storages.db.tables import Block, Transaction
from sbds.storages.db import Blocks, Transactions

logger = getLogger(__name__)


url = os.environ.get('STEEMD_HTTP_URL')
rpc = SimpleSteemAPIClient(url=url)
database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url, execution_options={'stream_results': True})



Session = sessionmaker(bind=engine)
session = Session()

def past_24_hours():
    return maya.now().iso8601(), maya.when('yesterday').iso8601()

def past_48_hours():
    return maya.now().iso8601(), maya.when('day before yesterday').iso8601()

def past_72_hours():
    return maya.now().iso8601(), maya.when('72 hours ago').iso8601()

'''
Accounts
=========
-  total accounts
SELECT COUNT(type) FROM sbds_transactions WHERE type='account_create'

-

'''



@route('/health')
def health():
    last_db_block = session.query(Block.block_num).order_by('block_num DESC').first()[0]
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    return dict(last_db_block=last_db_block,
                last_irreversible_block=last_irreversible_block,
                diff=diff,
                timestamp=datetime.utcnow().isoformat())



# Development server
@click.command()
def dev_server():
    run(host='0.0.0.0', port=8080, debug=True)


# WSGI application
app = application = bottle.default_app()