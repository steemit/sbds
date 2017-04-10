# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

# pylint: disable=import-error, unused-import
import bottle
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

from sbds.server.jsonrpc import register_endpoint
from sbds.server.methods import count_operations
from sbds.server.methods import get_custom_json_by_tid
from sbds.server.methods import get_random_operation_block_nums
from sbds.server.methods import get_random_operations
logger = sbds.sbds_logging.getLogger(__name__)

app = bottle.Bottle()
app.config['sbds.RPC_URL'] = os.environ.get('STEEMD_HTTP_URL',
                                            'https://steemd.steemitdev.com')
app.config['sbds.DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///')
app.config['sbds.MAX_BLOCK_NUM_DIFF'] = 10
app.config['sbds.MAX_DB_ROW_RESULTS'] = 100000
app.config['sbds.DB_QUERY_LIMIT'] = app.config['sbds.MAX_DB_ROW_RESULTS'] + 1
app.config['sbds.tx_class_map'] = tx_class_map
app.config['sbds.logger'] = logger

rpc = SimpleSteemAPIClient(app.config['sbds.RPC_URL'])


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


app.install(
    bottle.JSONPlugin(
        json_dumps=lambda s: json.dumps(s, cls=ToStringJSONEncoder)))
app.install(ErrorsRestPlugin())
db_plugin = get_db_plugin(app.config['sbds.DATABASE_URL'])
app.install(db_plugin)


# Non JSON-RPC routes
# -------------------
@app.get('/health')
def health(db):
    last_db_block = Block.highest_block(db)
    last_irreversible_block = rpc.last_irreversible_block_num()
    diff = last_irreversible_block - last_db_block
    if diff > app.config['sbds.MAX_BLOCK_NUM_DIFF']:
        abort(
            500,
            'last irreversible block (%s) - highest db block (%s) = %s, > max allowable difference (%s)'
            % (last_irreversible_block, last_db_block, diff,
               app.config['sbds.MAX_BLOCK_NUM_DIFF']))
    else:
        return dict(
            last_db_block=last_db_block,
            last_irreversible_block=last_irreversible_block,
            diff=diff,
            timestamp=datetime.utcnow().isoformat())


@app.get('/api/v1/blockchainStats')
def stats(db):
    results = blockchain_stats_query(db)
    return results


# JSON-RPC route
# --------------
jsonrpc = register_endpoint(path='/', app=app, namespace='sbds')

# All sbds methods registered here MUST have a name that begins with 'sbds.'
jsonrpc.register_method(
    method=count_operations, method_name='count_operations')
jsonrpc.register_method(
    method=get_custom_json_by_tid, method_name='get_custom_json_by_tid')
jsonrpc.register_method(
    method=get_random_operation_block_nums,
    method_name='get_random_operation_block_nums')
jsonrpc.register_method(
    method=get_random_operations, method_name='get_random_operations')


# WSGI application
# ----------------
application = app


# dev/debug server
# ----------------
def _dev_server(port=8080, debug=True):
    # pylint: disable=bare-except
    try:
        app.run(port=port, debug=debug)
    except:
        logger.exception('HTTP Server Exception')
    finally:
        app.close()


# For pdb debug only
if __name__ == '__main__':
    _dev_server()
