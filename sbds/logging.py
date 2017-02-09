# coding=utf-8
import logging
import time
import os

from pythonjsonlogger import jsonlogger

LOG_LEVEL = os.environ.get('SBDS_LOG_LEVEL', 'info').lower()

log_level_map = dict(debug=logging.DEBUG,
                 info=logging.INFO)
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
