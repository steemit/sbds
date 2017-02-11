# -*- coding: utf-8 -*-
import os
from datetime import datetime

import bottle
import click
from bottle import route, run
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine

from sbds.http_client import SimpleSteemAPIClient
from sbds.logging import getLogger
from sbds.storages.db import Base, Session
from sbds.storages.db.tables.core import Block

logger = getLogger(__name__)

url = os.environ.get('STEEMD_HTTP_URL')
rpc = SimpleSteemAPIClient(url=url)
database_url = os.environ.get('DATABASE_URL')
engine = create_engine(database_url, execution_options={'stream_results': True})

Session.configure(bind=engine)

app = bottle.Bottle()
plugin = sqlalchemy.Plugin(
        engine,  # SQLAlchemy engine created with create_engine function.
        Base.metadata,  # SQLAlchemy metadata, required only if create=True.
        keyword='db',
        # Keyword used to inject session database in a route (default 'db').
        create=False,
        # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
        commit=False,
        # If it is true, plugin commit changes after route is executed (default True).
        use_kwargs=False
        # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
)
app.install(plugin)

'''
Accounts
=========
-  total accounts
SELECT COUNT(type) FROM sbds_transactions WHERE type='account_create'

-

'''


@route('/health')
def health(db):
    last_db_block = \
        db.query(Block.block_num).order_by('block_num DESC').first()[0]
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    return dict(last_db_block=last_db_block,
                last_irreversible_block=last_irreversible_block,
                diff=diff,
                timestamp=datetime.utcnow().isoformat())


@app.get('/accounts/stats/:window')
def show(name, db):
    pass
    # entity = db.query(Account).filter_by(name=name).first()
    # if entity:
    #    return {'id': entity.id, 'name': entity.name}
    # return HTTPError(404, 'Entity not found.')


# Development server
@click.command()
def dev_server():
    run(host='0.0.0.0', port=8080, debug=True)


# WSGI application
application = app
