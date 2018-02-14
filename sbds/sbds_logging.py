# coding=utf-8
import logging
import sys

import structlog

from .sbds_json import dumps


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(serializer=dumps)
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

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
