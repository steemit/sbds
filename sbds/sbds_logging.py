# coding=utf-8
import logging
import os
import time

from pythonjsonlogger import jsonlogger


def make_log_format(x):
    return ['%({0:s})'.format(i) for i in x]


def get_current_log_level():
    return log_level_from_str(os.environ.get(SBDS_LOG_LEVEL_ENV_VAR_NAME))


def configure_root_logger(stream=True):
    root_logger = logging.getLogger()
    # remove all other handlers from root logger
    for hdlr in root_logger.handlers:
        root_logger.removeHandler(hdlr)
    if stream:
        hdlr = logging.StreamHandler()
        hdlr.set_name('root')
        hdlr.setLevel(logging.DEBUG)
        root_logger.addHandler(hdlr)
    return root_logger


def configure_log_handler(supported_log_message_keys, log_datetime_format):
    log_format = ' '.join(make_log_format(supported_log_message_keys))
    formatter = jsonlogger.JsonFormatter(
        fmt=log_format, datefmt=log_datetime_format)
    # set all datetimes to utc
    formatter.converter = time.gmtime

    log_handler = logging.StreamHandler()
    log_handler.set_name('sbds')
    log_handler.setFormatter(formatter)
    return log_handler


def log_level_from_str(log_level_str):
    level = SBDS_DEFAULT_LOG_LEVEL
    # pylint: disable=bare-except, lost-exception
    try:
        level = getattr(logging, log_level_str.upper())
    except:
        pass
    finally:
        return level


# configure root logger and logging
SBDS_LOG_LEVEL_ENV_VAR_NAME = 'SBDS_LOG_LEVEL'
SBDS_DEFAULT_LOG_LEVEL = logging.INFO
SBDS_LOG_DATETIME_FORMAT = r'%Y-%m-%dT%H:%M:%S.%s%Z'
SBDS_SUPPORTED_LOG_MESSAGE_KEYS = (
    'levelname',
    'asctime',
    #'created',
    'filename',
    # 'levelno',
    'module',
    'funcName',
    'lineno',
    'msecs',
    'message',
    'name',
    'pathname',
    'process',
    'processName',
    # 'relativeCreated',
    #'thread',
    'threadName')
SBDS_LOG_HANDLER = configure_log_handler(SBDS_SUPPORTED_LOG_MESSAGE_KEYS,
                                         SBDS_LOG_DATETIME_FORMAT)
SBDS_LOG_LEVEL = get_current_log_level()
SBDS_ROOT_LOGGER = configure_root_logger()

ROLLBAR_HANDLER = None
if 'SBDS_ROLLBAR_API_KEY' in os.environ:
    import rollbar
    from .rollbar_logger import RollbarHandler

    env = os.environ.get('SBDS_ENVIRONMENT', 'DEV')
    rollbar.init(os.environ.get('SBDS_ROLLBAR_API_KEY'), environment=env)
    rollbar_handler = RollbarHandler()
    rollbar_formatter = logging.Formatter()
    rollbar_handler.setFormatter(rollbar_formatter)
    rollbar_handler.set_name('rollbar')
    rollbar_handler.setLevel(logging.ERROR)
    ROLLBAR_HANDLER = rollbar_handler

# functions to configure other loggers


def getLogger(name,
              log_handler=SBDS_LOG_HANDLER,
              _rollbar_handler=ROLLBAR_HANDLER,
              level=None):
    _logger = logging.getLogger(name)
    handler_names = [h.name for h in _logger.handlers]
    if 'sbds' not in handler_names:
        level = level or get_current_log_level()
        _logger.setLevel(level)
        _logger.addHandler(log_handler)
        _logger.propagate = False
    if _rollbar_handler and 'rollbar' not in handler_names:
        _logger.addHandler(_rollbar_handler)
    return _logger


def configure_existing_logger(logger, log_handler=None, level=None):
    log_handler = log_handler or SBDS_LOG_HANDLER
    level = level or get_current_log_level()
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)
    logger.addHandler(log_handler)
    logger.setLevel(level)
    return logger


def session_to_dict(session):
    return dict(
        session_info=session.info,
        session_dirty_count=len(session.dirty),
        session_new_count=len(session.new),
        session_is_active=session.is_active,
        session_transaction_parent=session.transaction.parent)


# handle logging of specific messages
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
        kwargs = dict(
            block_num=getattr(obj, 'block_num', None),
            transaction_num=getattr(obj, 'transaction_num', None),
            operation_num=getattr(obj, 'operation_num', None),
            cls=obj.__class__,
            object_name=obj.__class__.__name__)
    except Exception as e:
        logger.error(e)
        return generate_fail_log(logger, object=obj)
    return generate_fail_log(logger, **kwargs)
