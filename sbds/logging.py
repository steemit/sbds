# coding=utf-8
import logging
import time
import os

from pythonjsonlogger import jsonlogger

LOG_LEVEL = os.environ.get('SBDS_LOG_LEVEL', 'info').lower()

log_level_map = dict(debug=logging.DEBUG,
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


def make_log_format(x):
    return ['%({0:s})'.format(i) for i in x]


# noinspection PyPep8Naming
def getLogger(name, level=_log_level):
    _logger = logging.getLogger(name)
    if not _logger.hasHandlers():
        _logger.setLevel(level)
        _logger.addHandler(logHandler)
    return _logger


def generate_fail_log(logger, **kwargs):
    logger.error('FAILED TO ADD %s', kwargs.get('name', 'item'), extra=kwargs)


def generate_fail_log_from_block_info(logger, block_info):
    kwargs = dict(
            block_num=block_info['block_num'],
            transactions=block_info['transactions'])
    return generate_fail_log(logger, **kwargs)


def generate_fail_log_from_raw_block(logger, raw_block):
    from sbds.utils import block_info
    info = block_info(raw_block)
    return generate_fail_log_from_block_info(logger, info)


def generate_fail_log_from_obj(logger, obj):
    try:
        kwargs = dict(block_num=getattr(obj, 'block_num', None),
                      transaction_num=getattr(obj, 'transaction_num', None),
                      operation_num=getattr(obj, 'operation_num', None),
                      cls=obj.__class__,
                      object_name=obj.__class__.__name__)
    except Exception as e:
        logger.error(e)
        return generate_fail_log(logger, object=obj)
    return generate_fail_log(logger, **kwargs)


# configure logging
fmt = ' '.join(make_log_format(supported_keys))
datefmt = r'%Y-%m-%dT%H:%M:%S.%s%Z'

root_logger = logging.getLogger()
for hdlr in root_logger.handlers:
    root_logger.removeHandler(hdlr)

formatter = jsonlogger.JsonFormatter(fmt=fmt, datefmt=datefmt)
formatter.converter = time.gmtime
logHandler = logging.StreamHandler()
logHandler.setFormatter(formatter)
