# -*- coding: utf-8 -*-
import random

from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db.tables.core import extract_operations_from_blocks
from .utils import query_response

# pylint: disable=unused-argument
def count_operations(db, bottle, app, params):
    # required params
    operation = params['operation']

    # optional params
    to = params.get('to')
    _from = params.get('_from')

    query = operation.count_query(db)
    query = operation.from_to_filter(query, _from=_from, to=to)
    return query.scalar()


# pylint: disable=unused-argument
def get_custom_json_by_tid(db, bottle, app, params):
    max_db_row_results = app.config['sbds.MAX_DB_ROW_RESULTS']
    db_query_hard_limit = app.config['sbds.DB_QUERY_LIMIT']
    custom_json_class = app.config['sbds.tx_class_map']['custom_json']

    # required params
    tid = params['tid']

    # optional params
    to = params.get('to')
    _from = params.get('_from')

    query = db.query(custom_json_class).filter_by(tid=tid)
    query = custom_json_class.from_to_filter(query, _from=_from, to=to)

    result = query.limit(db_query_hard_limit).all()
    return query_response(result, max_db_row_results)


def get_random_operation_block_nums(db, bottle, app, params):
    """Return a random sample of block_nums containing specified operation.

    Args:
        db ():
        bottle ():
        app ():
        params ():

    Returns:

    """
    op_type = params.get('op_type')
    op_count = params.get('count', 100)
    op_class = app.config['sbds.tx_class_map'][op_type]
    results = db.query(op_class.block_num).all()
    if op_count > len(results):
        op_count = len(results)
    block_nums = [r[0] for r in random.sample(results, op_count)]
    return block_nums

# pylint: disable=unsubscriptable-object
def get_random_operations(db, bottle, app, params):
    """Return a random sample of specified operation.

    Args:
        db ():
        bottle ():
        app ():
        params ():

    Returns:

    """

    op_type = params.get('op_type')
    op_count = params.get('count', 100)
    op_class = app.config['sbds.tx_class_map'][op_type]
    db_query_hard_limit = app.config['sbds.DB_QUERY_LIMIT']

    results = db.query(op_class.block_num).limit(db_query_hard_limit).all()
    if op_count > 1000:
        op_count = 1000
    if op_count > len(results):
        op_count = len(results)
    block_nums = [r[0] for r in random.sample(results, op_count)]
    client = SimpleSteemAPIClient()
    blocks = map(client.get_block, block_nums)
    ops = extract_operations_from_blocks(blocks)
    filtered_ops = filter(lambda op: op.get('type') == op_type, ops)
    return list(filtered_ops)
