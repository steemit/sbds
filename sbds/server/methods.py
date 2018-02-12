# -*- coding: utf-8 -*-

from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db.tables.core import extract_operations_from_blocks


# pylint: disable=unused-argument
def count_operations(operation, to=None, _from=None, context=None):
    request = context['request']
    db = request.config.db
    query = operation.count_query(db)
    query = operation.from_to_filter(query, _from=_from, to=to)
    return query.scalar()


# pylint: disable=unused-argument
def get_custom_json_by_tid(tid, to, _from, context=None):
    request = context['request']
    db = request.config.db
    db_query_hard_limit = request.config['sbds.DB_QUERY_LIMIT']
    custom_json_class = request.config['sbds.tx_class_map']['custom_json']

    query = db.query(custom_json_class).filter_by(tid=tid)
    query = custom_json_class.from_to_filter(query, _from=_from, to=to)
    return query.limit(db_query_hard_limit).all()
