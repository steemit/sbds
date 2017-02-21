# -*- coding: utf-8 -*-
import os
from datetime import datetime
import logging

import click
import bottle
from bottle.ext import sqlalchemy
from bottle import request

import maya

import sbds.logging
from sbds.http_client import SimpleSteemAPIClient

from sbds.storages.db import Base, Session
from sbds.storages.db.tables.core import Block
from sbds.storages.db.tables.tx import tx_class_map
from sbds.storages.db.utils import configure_engine

MAX_DB_ROW_RESULTS = 100000
DB_QUERY_LIMIT = MAX_DB_ROW_RESULTS + 1

logger = sbds.logging.getLogger(__name__, level=logging.DEBUG)

rpc_url = os.environ.get('STEEMD_HTTP_URL', 'https://steemd.steemitdev.com')
database_url = os.environ.get('DATABASE_URL', 'sqlite:///')

rpc = SimpleSteemAPIClient(rpc_url)

database_url, url, engine_kwargs, engine = configure_engine(
    database_url, echo=True)
Session.configure(bind=engine)

app = bottle.Bottle()
# pylint: disable=undefined-variable
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
    create_session=Session)
# pylint: enable=undefined-variable

app.install(plugin)
'''
Accounts
=========
-  total accounts
SELECT COUNT(type) FROM sbds_transactions WHERE type='account_create'

-

'''


def match_operation(op_str):
    return tx_class_map[op_str.lower()]


# pylint: disable=unused-argument
def operation_filter(config):
    ''' Matches blockchain operations. '''

    regexp = '(%s){1}' % r'|'.join(key for key in tx_class_map.keys())

    def to_python(match):
        return tx_class_map[match]

    def to_url(tx):
        return tx.operation_type

    return regexp, to_python, to_url


# pylint: enable=unused-argument

app.router.add_filter('operations', operation_filter)


class JSONError(bottle.HTTPResponse):
    default_status = 500

    def __init__(self,
                 status=None,
                 body=None,
                 exception=None,
                 traceback=None,
                 **options):
        self.exception = exception
        self.traceback = traceback
        body = dict(error=body)
        headers = {'Content-Type': 'application/json'}
        super(JSONError, self).__init__(
            body, status, headers=headers, **options)


def parse_block_num(block_num):
    return int(block_num)


def parse_iso8601(iso_str):
    return maya.dateparser.parse(iso_str)


def parse_to_query_field(to=None):
    if isinstance(to, tuple):
        to = to[0]
    elif isinstance(to, int):
        return parse_block_num(to)
    elif isinstance(to, str):
        try:
            return parse_block_num(to)
        except ValueError:
            return parse_iso8601(to)
    else:
        raise ValueError('to must be a iso8601 string or block_num')


def parse_from_query_field(_from=None):
    if isinstance(_from, tuple):
        _from = _from[0]
    elif isinstance(_from, int):
        return parse_block_num(_from)
    elif isinstance(_from, str):
        try:
            return parse_block_num(_from)
        except ValueError:
            return parse_iso8601(_from)
    else:
        raise ValueError('from must be a iso8601 string or block_num')


query_field_parser_map = {
    'to': parse_to_query_field,
    'from': parse_from_query_field
}


def parse_query_fields(query_dict):
    logger.debug('query_dict', extra=query_dict)
    parsed_fields = dict()
    for key, value in query_dict.items():
        if key in query_field_parser_map:
            parsed_fields[key] = query_field_parser_map[key](value)
        else:
            raise ValueError('received unknown query field: %s', key)

    logger.debug('parsed_fields', extra=parsed_fields)
    return parsed_fields


def return_query_response(result):
    if len(result) > MAX_DB_ROW_RESULTS:
        return JSONError(
            status=403, body='Too many results (%s rows)' % len(result))
    else:
        return [row.to_json() for row in result]


@app.get('/health')
def health(db):
    last_db_block = Block.highest_block(db)
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    return dict(
        last_db_block=last_db_block,
        last_irreversible_block=last_irreversible_block,
        diff=diff,
        timestamp=datetime.utcnow().isoformat())


@app.get('/api/v1/ops/<operation:operations>/count')
def count_operation(operation, db):
    query = db.query(operation)
    if request.query:
        try:
            parsed_fields = parse_query_fields(request.query)
        except Exception as e:
            return JSONError(status=400, body='Bad query: %s' % e)
        _from = parsed_fields.get('from')
        to = parsed_fields.get('to')
        query = operation.from_to_filter(query, _from=_from, to=to)

    return dict(count=query.count())


# '/api/v1/ops/custom/:tid?from=<iso8601-or-block_num>&to=<iso8601-or-blocknum>'
@app.get('/api/v1/ops/custom/:tid')
def get_custom_json_by_tid(tid, db):
    cls = tx_class_map['custom']
    query = db.query(cls).filter_by(tid=tid)
    if request.query:
        try:
            parsed_fields = parse_query_fields(request.query)
        except Exception as e:
            logger.error(e)
            return JSONError(status=400, body='Bad query: %s' % e)

        query = cls.from_to_filter(
            query, _from=parsed_fields.get('from'), to=parsed_fields.get('to'))
    return return_query_response(result)


# Development server
@click.command()
def dev_server():
    _dev_server()


def _dev_server():
    # pylint: disable=bare-except
    try:
        app.run(port=8080, debug=True)
    except:
        pass
    finally:
        app.close()


# pylint: enable=bare-except

# WSGI application
application = app
