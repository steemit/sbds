# -*- coding: utf-8 -*-
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
