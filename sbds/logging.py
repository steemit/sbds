import logging
import json
import time

from pythonjsonlogger import jsonlogger


supported_keys = [
            'asctime',
            'created',
            'filename',
            'funcName',
            'levelname',
            #'levelno',
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

def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = jsonlogger.JsonFormatter(fmt=fmt, datefmt=datefmt)
    formatter.converter = time.gmtime
    logHandler = logging.StreamHandler()
    logHandler.setFormatter(formatter)
    logger.handlers=[logHandler]
    return logger
