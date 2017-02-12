# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

import bottle
from bottle.ext import sqlalchemy
import click
from bottle import route, run

from bottle import HTTPError

import maya

from sbds.http_client import SimpleSteemAPIClient
from sbds.logging import getLogger
from sbds.storages.db.utils import configure_engine
from sbds.storages.db import Base, Session
from sbds.storages.db.tables.core import Block
from sbds.storages.db.tables.tx import tx_class_map


logger = getLogger(__name__)

rpc_url = os.environ.get('STEEMD_HTTP_URL', 'https://steemd.steemitdev.com')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///')

rpc = SimpleSteemAPIClient(rpc_url)

database_url, url, engine_kwargs, engine = configure_engine(database_url, echo=True)
Session.configure(bind=engine)


app = bottle.Bottle()
plugin = sqlalchemy.Plugin(
        engine,  # SQLAlchemy engine created with create_engine function.
        Base.metadata,  # SQLAlchemy metadata, required only if create=True.
        keyword='db',
        # Keyword used to inject session database in a route (default 'db').
        create=True,
        # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
        commit=False,
        # If it is true, plugin commit changes after route is executed (default True).
        use_kwargs=False,
        # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
        create_session=Session
)
app.install(plugin)

'''
Accounts
=========
-  total accounts
SELECT COUNT(type) FROM sbds_transactions WHERE type='account_create'

-

'''

TIME_WINDOWS = (
    'past-24-hours',
    'past-48-hours',
    'past-72-hours',
    'past-24-to-48-hours',
    'past-48-to-72-hours',
)

def match_time_windows(window_str):
    if window_str in TIME_WINDOWS:
        return window_str
    try:
        f, _from, t, to = window_str.split()
        return maya.dateparser.parse(_from), maya.dateparser.parse(to)
    except ValueError:
        return None


def match_operation(op_str):
    return tx_class_map[op_str.lower()]

class JSONError(bottle.HTTPResponse):
    default_status = 500

    def __init__(self, status=None, body=None, exception=None, traceback=None,
                 **options):
        self.exception = exception
        self.traceback = traceback
        body = dict(error=body)
        headers = {'Content-Type': 'application/json'}
        super(JSONError, self).__init__(body, status, headers=headers, **options)


@app.get('/health')
def health(db):
    last_db_block = Block.highest_block(db)
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    return dict(last_db_block=last_db_block,
                last_irreversible_block=last_irreversible_block,
                diff=diff,
                timestamp=datetime.utcnow().isoformat())





@app.get('/count/:operation')
def count_operation(operation,  db):
    try:
        cls = match_operation(operation)
    except KeyError:
        return JSONError(status=404,
                         body='Operation not found. Posssible operations: %s' %
                         list(tx_class_map.keys()))

    _from, to, query = cls.past_24(db)
    if _from:
        _from = _from.isoformat()
    if to:
        to = to.isoformat()
    return dict(from_datetime=_from,
                to_datetime=to,
                count=query.count())


@app.get('/sum/:operation')
def sum_operation(operation,  db):
    try:
        cls = match_operation(operation)
    except KeyError:
        return JSONError(status=404,
                         body='Operation not found. Posssible operations: %s' %
                         list(tx_class_map.keys()))

    _from, to, query = cls.past_24(db)
    if _from:
        _from = _from.isoformat()
    if to:
        to = to.isoformat()
    return dict(from_datetime=_from,
                to_datetime=to,
                count=query.count())


# Development server
@click.command()
def dev_server():
    _dev_server()

def _dev_server():
    app.run(port=8080, debug=True)

# WSGI application
application = app
