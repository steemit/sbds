# -*- coding: utf-8 -*-
from collections import Counter
from itertools import chain
from collections import namedtuple
from contextlib import contextmanager

import toolz.itertoolz
from sqlalchemy.exc import IntegrityError
from toolz.itertoolz import partition_all
from sqlalchemy.orm.util import object_state

import sbds.logging
from sbds.utils import block_info
from sbds.utils import write_json
from .tables import Base
from .tables import Session
from .tables.core import from_raw_block
from .utils import is_duplicate_entry_error
from .utils import new_session
from .utils import session_scope

metadata = Base.metadata

logger = sbds.logging.getLogger(__name__)



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


def safe_merge_insert(objects, session, load=True):
    with session_scope(session) as s:
        for object in objects:
            session.merge(object, load=load)
    return all([object_state(object).persistent for object in objects])

def safe_insert(object, session):
    with session_scope(session) as s:
        s.add(object)
    result =  object_state(object).persistent
    if not result:
        generate_fail_log_from_obj(object)

def safe_insert_many(objects, session):
    with session_scope(session) as s:
        s.add_all(objects)

    return object_state(objects[0]).persistent


def adaptive_insert(objects, session, bulk=False, insert_many=True,
                    merge_insert=True):
    if not objects:
        return True
    if bulk:
        # attempt bulk save if
        logger.debug('attepmting bulk_save')
        with session_scope(session) as s:
            s.bulk_save_objects(objects)
        if object_state(objects[0]).persistent:
            logger.debug('bulk_save success')
            return True
        else:
            logger.debug('bulk_save failed')

    if insert_many:
        # attempt insert_many
        if safe_insert_many(objects, session):
            logger.debug('attepmting safe_insert_many')
            return True
        else:
            logger.debug('safe_insert_many failed')

    if merge_insert:
        # attempt safe_merge_insert
        logger.debug('attempting safe_merge_insert')
        if safe_merge_insert(objects, session):
            logger.debug('safe_merge_insert success')
            return True
        else:
            logger.debug('safe_merge_insert failed')

    # fallback to safe_insert each object
    logger.debug('attempting individual safe_insert')
    results = [safe_insert(object, session) for object in objects]
    for i,result in enumerate(results):
        if not result:
            object = objects[i]
            generate_fail_log_from_obj(object)
    return results

def add_block(raw_block, session, info=None):
    """
    :param raw_block: str
    :param session:
    :param info: dict
    :return: boolean
    """
    block_obj, txtransactions = from_raw_block(raw_block, session)
    result = adaptive_insert(list([block_obj, *txtransactions]), session)
    if isinstance(result, bool):
        return result
    else:
        return all(result)

def filter_existing_blocks(block_objects, session):
    """
    :param block_objects: list
    :param session:
    :return:
    """
    from .tables import Block
    results = session.query(Block.block_num) \
        .filter(Block.block_num.in_([b.block_num for b in block_objects])).all()
    if results:
        results = [r[0] for r in results]
        logger.info('found existing blocks: %s', len(results))
        filtered_block_objs = [b for b in block_objects if
                               b.block_num not in results]
        logger.info('removed %s existing objects from list',
                    len(block_objects) - len(filtered_block_objs))
        return filtered_block_objs
    return block_objects


def add_blocks(raw_blocks,
               session,
               offset=0):
    """
    :param raw_blocks: list
    :param session:
    :param offset: int
    """
    if offset != 0:
        raw_blocks = toolz.itertoolz.drop(offset, raw_blocks)

    for raw_block in raw_blocks:
        result = add_block(raw_block, session)
        if not result:
            generate_fail_log_from_raw_block(raw_block)




def bulk_add(raw_blocks, session):
    """
    :param raw_blocks: list
    :param session:
    """
    from .tables import Block
    from .tables import TxBase

    raw_blocks_chunk = list(raw_blocks)

    block_objs = list(map(Block.from_raw_block, raw_blocks_chunk))
    tx_objs = list(
            chain.from_iterable(
                    map(TxBase.from_raw_block, raw_blocks_chunk)))

    # remove existing to avoid IntegrityError
    block_objs = filter_existing_blocks(block_objs, session)

    # add blocks (only if we havent removed them all)
    if block_objs:
        adaptive_insert(block_objs, session, bulk=True)

    # add txs
    adaptive_insert(tx_objs, session, bulk=True)