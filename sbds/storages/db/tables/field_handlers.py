# -*- coding: utf-8 -*-
import json

import sbds.logging

logger = sbds.logging.getLogger(__name__)

def json_metadata(value):
    if not value:
        return None
    metadata = metadata2 = None
    try:
        metadata = json.loads(value)
        if isinstance(metadata, dict):
           return metadata
        elif isinstance(metadata, str):
            if metadata == "":
                return None
            else:
                metadata2 = json.loads(metadata)
                return metadata
    except Exception as e:
        extra = dict(original=value, metadata=metadata, metadata2=metadata2, error=e)
        logger.error('json_metadata handler error', extra=extra)
        return None

def amount(value, num_func=int, no_value=0):
    if not value:
        return num_func(no_value)
    try:
        return num_func(value.split()[0])
    except Exception as e:
        extra = dict(original=value, num_func=num_func, no_value=no_value, error=e)
        logger.error('amount handler error', extra=extra)
        return num_func(no_value)

def amount_symbol(value, no_value=''):
    if not value:
        return no_value
    try:
        return value.split()[1]
    except Exception as e:
        extra = dict(original=value,  no_value=no_value, error=e)
        logger.error('amount_symbol handler error', extra=extra)
        return no_value

def comment_body(value):
    print('comment_body type:%s value:%s' % (type(value), value))
    if isinstance(value, bytes):
        return value.decode('utf8')
    else:
        return value