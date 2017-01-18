# coding=utf-8
import logging
import time
import sys

from pythonjsonlogger import jsonlogger

supported_keys = [
    'asctime',
    'created',
    'filename',
    'funcName',
    'levelname',
    # 'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'thread',
    'threadName'
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

def getLogger(name):
    logger = logging.getLogger(name)
    #print('name:%s, logger:%s, handlers:%s' % (name, logger, logger.handlers), file=sys.stderr)
    if not logger.hasHandlers():
        #print('adding handler to %s' % name, file=sys.stderr)
        logger.setLevel(logging.INFO)
        logger.addHandler(logHandler)
    return logger
