# -*- coding: utf-8 -*-
from functools import singledispatch

import maya
import funcy

import sbds.sbds_logging
from sbds.storages.db.tables.tx import tx_class_map

logger = sbds.sbds_logging.getLogger(__name__)


@funcy.log_calls(logger.debug, errors=True)
def parse_operation(op_str):
    return tx_class_map[op_str.lower()]


@funcy.log_calls(logger.debug, errors=True)
def parse_op_type(op_str):
    if op_str in tx_class_map:
        return op_str
    else:
        raise ValueError('"op_type" must be a valid steem operation')


@funcy.log_calls(logger.debug, errors=True)
@singledispatch
def parse_to_from(value):
    if not value:
        return
    else:
        raise ValueError('must be an iso8601 string or int')


@parse_to_from.register(int)
def parse_block_num(value):
    return int(value)


@parse_to_from.register(str)
def parse_iso8601(value):
    return maya.dateparser.parse(value)


# pylint: disable=unnecessary-lambda
param_parser_map = {
    'to': parse_to_from,
    'from': parse_to_from,
    'operation': parse_operation,
    'op_type': parse_op_type,
    'count': lambda count: int(count),
    'tid': lambda tid: tid
}


@funcy.log_calls(logger.debug, errors=True)
@singledispatch
def parse_params(params):
    if not params:
        return
    else:
        raise ValueError('params must be dict or list')


@parse_params.register(dict)
def parse_params_dict(params):
    parsed_fields = dict()
    for key, value in params.items():
        if key in param_parser_map:
            parsed_fields[key] = param_parser_map[key](value)
        else:
            raise ValueError('received unknown param: %s', key)
    logger.debug('parsed_fields', extra=parsed_fields)
    return parsed_fields


@parse_params.register(list)
def parse_params_list(value):
    return value
