# -*- coding: utf-8 -*-
import maya
import funcy

import sbds.sbds_logging
from sbds.storages.db.tables.tx import tx_class_map

logger = sbds.sbds_logging.getLogger(__name__)


# pylint: disable=unused-argument
def operation_filter(config):
    ''' Matches blockchain operations. '''
    regexp = '(%s){1}' % r'|'.join(key for key in tx_class_map.keys())

    def to_python(match):
        return tx_class_map[match]

    def to_url(tx):
        return tx.operation_type

    return regexp, to_python, to_url


def match_operation(op_str):
    return tx_class_map[op_str.lower()]


def parse_block_num(block_num):
    return int(block_num)


def parse_iso8601(iso_str):
    return maya.dateparser.parse(iso_str)


@funcy.log_calls(logger.debug, errors=True)
def parse_to_query_field(to=None):
    extra = dict(query_field='to', value=to, value_type=type(to))
    if isinstance(to, tuple):
        to = to[0]
    elif isinstance(to, int):
        result = parse_block_num(to)
        logger.debug('parsed query field "to" result %s', result, extra=extra)
        return result
    elif isinstance(to, str):
        try:
            parse_block_num(to)
        except ValueError:
            return parse_iso8601(to)
    else:
        raise ValueError('to must be a iso8601 string or block_num')


@funcy.log_calls(logger.debug, errors=True)
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


@funcy.log_calls(logger.debug, errors=True)
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
