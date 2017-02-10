# coding=utf-8
import logging
import time
import os

from pythonjsonlogger import jsonlogger

from sbds.storages.db import logger
from sbds.utils import block_info

LOG_LEVEL = os.environ.get('SBDS_LOG_LEVEL', 'info').lower()

log_level_map = dict(   debug=logging.DEBUG,
                        info=logging.INFO,
                        warning=logging.WARNING,
                        error=logging.ERROR
                     )

_log_level = log_level_map.get(LOG_LEVEL, logging.INFO)

supported_keys = [
    'levelname',
    # 'asctime',
    # 'created',
    # 'filename',


    # 'levelno',

    'module',
    'funcName',
    'lineno',
    # 'msecs',
    'message',
    # 'name',
    # 'pathname',
    # 'process',
    # 'processName',
    # 'relativeCreated',
    # 'thread',
    # 'threadName'
]



log_format = lambda x: ['%({0:s})'.format(i) for i in x]
fmt = ' '.join(log_format(supported_keys))
datefmt = r'%Y-%m-%dT%H:%M:%S.%s%Z'

logger = logging.getLogger()
for hdlr in logger.handlers:
    logger.removeHandler(hdlr)

formatter = jsonlogger.JsonFormatter(fmt=fmt, datefmt=datefmt)
formatter.converter = time.gmtime
logHandler = logging.StreamHandler()
logHandler.setFormatter(formatter)


# noinspection PyPep8Naming
def getLogger(name, level=_log_level):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(level)
        logger.addHandler(logHandler)
    return logger


def generate_fail_log(**kwargs):
    logger.error('FAILED TO ADD %s', kwargs.get('name', 'item'), extra=kwargs)


def generate_fail_log_from_block_info(block_info):
    kwargs = dict(block_num=block_info['block_num'],
                  transactions=block_info['transactions'])
    return generate_fail_log(**kwargs)


def generate_fail_log_from_raw_block(raw_block):
    info = block_info(raw_block)
    return generate_fail_log_from_block_info(info)


def generate_fail_log_from_obj(object):
    try:
        kwargs = dict(block_num=getattr(object, 'block_num', None),
                     transaction_num=getattr(object, 'transaction_num', None),
                     operation_num=getattr(object, 'operation_num', None),
                     cls=object.__class__,
                    object_name=object.__class__.__name__
                     )
    except Exception as e:
        logger.error(e)
        return generate_fail_log(object=object)
    return generate_fail_log(**kwargs)