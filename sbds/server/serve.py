# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

import bottle
# pylint: disable=import-error
from bottle.ext import sqlalchemy
# pylint: enable=import-error
from bottle import request
from bottle import abort
from bottle_errorsrest import ErrorsRestPlugin

import sbds.sbds_logging
from sbds.http_client import SimpleSteemAPIClient

from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session
from sbds.storages.db.tables.core import Block
from sbds.storages.db.tables.tx import tx_class_map
from sbds.storages.db.query_helpers import blockchain_stats_query
from sbds.storages.db.utils import configure_engine
from sbds.sbds_json import ToStringJSONEncoder

from sbds.server.utils import return_query_response
from sbds.server.input_parsers import operation_filter
from sbds.server.input_parsers import parse_query_fields

logger = sbds.sbds_logging.getLogger(__name__)

RPC_URL = os.environ.get('STEEMD_HTTP_URL', 'https://steemd.steemitdev.com')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///')
MAX_BLOCK_NUM_DIFF = 10
MAX_DB_ROW_RESULTS = 100000
DB_QUERY_LIMIT = MAX_DB_ROW_RESULTS + 1

rpc = SimpleSteemAPIClient(RPC_URL)


def get_db_plugin(database_url):
    engine_config = configure_engine(database_url)
    Session.configure(bind=engine_config.engine)

    # pylint: disable=undefined-variable
    return sqlalchemy.Plugin(
        # SQLAlchemy engine created with create_engine function.
        engine_config.engine,

        # SQLAlchemy metadata, required only if create=True.
        Base.metadata,

        # Keyword used to inject session database in a route (default 'db').
        keyword='db',

        # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
        create=True,

        # If it is true, plugin commit changes after route is executed (default True).
        commit=False,
        # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
        use_kwargs=False,
        create_session=Session)


app = bottle.Bottle()
app.install(
    bottle.JSONPlugin(
        json_dumps=lambda s: json.dumps(s, cls=ToStringJSONEncoder)))
app.install(ErrorsRestPlugin())
app.router.add_filter('operations', operation_filter)
db_plugin = get_db_plugin(DATABASE_URL)
app.install(db_plugin)


@app.get('/health')
def health(db):
    last_db_block = Block.highest_block(db)
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    if diff > MAX_BLOCK_NUM_DIFF:
        abort(
            500,
            'difference between blockchain last irreversible block (%s) and highest db block (%s) is %s which exceeds max allowable difference of %s'
            % (last_irreversible_block, last_db_block, diff,
               MAX_BLOCK_NUM_DIFF))
    else:
        return dict(
            last_db_block=last_db_block,
            last_irreversible_block=last_irreversible_block,
            diff=diff,
            timestamp=datetime.utcnow().isoformat())


@app.get('/api/v1/ops/<operation:operations>/count')
def count_operation(operation, db):
    query = operation.count_query(db)
    if request.query:
        try:
            parsed_fields = parse_query_fields(request.query)
        except Exception as e:
            abort(400, 'Bad query: %s' % e)
        else:
            _from = parsed_fields.get('from')
            to = parsed_fields.get('to')
            query = operation.from_to_filter(query, _from=_from, to=to)
    return dict(count=query.scalar())


@app.get('/api/v1/blockchainStats')
def stats(db):
    results = blockchain_stats_query(db)
    return results


# '/api/v1/ops/custom/:tid?from=<iso8601-or-block_num>&to=<iso8601-or-blocknum>'
@app.get('/api/v1/ops/custom_json/:tid')
def get_custom_json_by_tid(tid, db):
    cls = tx_class_map['custom_json']
    query = db.query(cls).filter_by(tid=tid)
    if request.query:
        try:
            parsed_fields = parse_query_fields(request.query)
        except Exception as e:
            logger.error(e)
            abort(400, 'Bad query: %s' % e)
        query = cls.from_to_filter(
            query, _from=parsed_fields.get('from'), to=parsed_fields.get('to'))

    result = query.limit(DB_QUERY_LIMIT).all()
    return return_query_response(result)


def _dev_server(port=8080, debug=True):
    # pylint: disable=bare-except
    try:
        app.run(port=port, debug=debug)
    except:
        logger.exception('HTTP Server Exception')
    finally:
        app.close()


# WSGI application
application = app

# For pdb debug only
if __name__ == '__main__':
    _dev_server()
