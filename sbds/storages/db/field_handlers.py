# -*- coding: utf-8 -*-
import sbds.sbds_logging
from sbds import sbds_json

logger = sbds.sbds_logging.getLogger(__name__)


def amount_field(value, num_func=int, no_value=0):
    if not value:
        return num_func(no_value)
    try:
        return num_func(value.split()[0])
    except Exception as e:
        extra = dict(
            original=value, num_func=num_func, no_value=no_value, error=e)
        logger.error('amount handler error', extra=extra)
        return num_func(no_value)


def amount_symbol_field(value, no_value=''):
    if not value:
        return no_value
    try:
        return value.split()[1]
    except Exception as e:
        extra = dict(original=value, no_value=no_value, error=e)
        logger.error('amount_symbol handler error', extra=extra)
        return no_value


def comment_body_field(value):
    if isinstance(value, bytes):
        return value.decode('utf8')
    return value


def json_string_field(value):
    if value:
        try:
            return sbds_json.dumps(value)
        except Exception as e:
            logger.exception(e)
            return None
