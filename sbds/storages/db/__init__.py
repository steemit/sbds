# -*- coding: utf-8 -*-
from itertools import chain
from itertools import zip_longest

import toolz.itertoolz
from sqlalchemy.orm.util import object_state

from sbds.logging import generate_fail_log_from_obj
from sbds.logging import generate_fail_log_from_raw_block
from sbds.logging import getLogger
from .tables import Base
from .tables import Session
from .tables.core import from_raw_block
from .utils import is_duplicate_entry_error
from .utils import new_session
from .utils import session_scope

metadata = Base.metadata

logger = getLogger(__name__)


# pylint: disable=bare-except,too-many-branches,too-many-arguments, unused-argument
def safe_merge_insert(objects, session, load=True, **kwargs):
    # pylint: disable=bare-except
    try:
        with session_scope(session, _raise=True) as s:
            for obj in objects:
                s.merge(obj, load=load)
    except:
        return False
    else:
        return True


def safe_insert(obj, session, log_fail=False, **kwargs):
    with session_scope(session, **kwargs) as s:
        s.add(obj)
    result = getattr(object_state(obj), 'persistent', False)
    if not result and log_fail:
        generate_fail_log_from_obj(logger, obj)


def safe_insert_many(objects, session, **kwargs):
    # noinspection PyBroadException
    try:
        with session_scope(session, _raise=True) as s:
            s.add_all(objects)
    except:
        return False
    else:
        return True


def safe_bulk_save(objects, session, **kwargs):
    # noinspection PyBroadException
    try:
        with session_scope(session, _raise=True) as s:
            s.bulk_save_objects(objects)
            s.commit()
    except:
        logger.debug('session.info: %s', session.info)
        return False
    else:
        return True


def adaptive_insert(objects,
                    session,
                    bulk=False,
                    insert_many=True,
                    merge_insert=True,
                    insert=True,
                    **kwargs):
    # pylint: disable=too-many-return-statements
    if not objects:
        logger.debug('adaptive_insert called with empty objects list')
        return True
    if bulk:
        # attempt bulk save if
        logger.debug('attempting bulk_save')
        if safe_bulk_save(objects, session, **kwargs):
            logger.debug('bulk_save success')
            return list(zip_longest(objects, list(), fillvalue=True))
        else:
            logger.info('bulk_save failed')

    if insert_many:
        # attempt insert_many
        if safe_insert_many(objects, session, **kwargs):
            logger.debug('attempting safe_insert_many')
            return list(zip_longest(objects, list(), fillvalue=True))
        else:
            logger.info('safe_insert_many failed')

    if merge_insert:
        # attempt safe_merge_insert
        logger.debug('attempting safe_merge_insert')
        if safe_merge_insert(objects, session, **kwargs):
            logger.debug('safe_merge_insert success')
            return list(zip_longest(objects, list(), fillvalue=True))
        else:
            logger.info('safe_merge_insert failed')

    # fallback to safe_insert each object
    logger.debug('attempting individual safe_insert')
    if insert:
        results = [safe_insert(obj, session, **kwargs) for obj in objects]
        if all(r for r in results):
            logger.debug('individual safe_insert success')
            return results

        # log failed objects
        failed = [obj for obj, r in zip(objects, results) if not r]
        logger.debug(
            'individual safe_insert results: failed to insert %s of %s objects',
            len(failed), len(objects))
        objects = failed

    # log failed objects
    for obj in objects:
        generate_fail_log_from_obj(logger, obj)

    logger.debug('adaptive_insert failed partially or completely')
    if insert:
        return results
    else:
        return list(zip_longest(objects, list(), fillvalue=False))


def add_block(raw_block, session, insert=False, **kwargs):
    """
    :param raw_block: str
    :param session:
    :return: boolean
    """
    block_obj, txtransactions = from_raw_block(raw_block, session)
    results = adaptive_insert(
        list([block_obj, *txtransactions]), session, insert=insert, **kwargs)
    return results


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

        logger.debug('found existing blocks: %s', len(results))
        filtered_block_objs = [
            b for b in block_objects if b.block_num not in results
        ]
        logger.debug('removed %s existing objects from list',
                     len(block_objects) - len(filtered_block_objs))
        return filtered_block_objs
    return block_objects


def add_blocks(raw_blocks, session, offset=0):
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
            generate_fail_log_from_raw_block(logger, raw_block)


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
        chain.from_iterable(map(TxBase.from_raw_block, raw_blocks_chunk)))

    # remove existing to avoid IntegrityError
    block_objs = filter_existing_blocks(block_objs, session)

    # add blocks (only if we havent removed them all)
    objs_to_add = [*block_objs, *tx_objs]
    results = adaptive_insert(objs_to_add, session, bulk=True)
    success_count = [r[1] for r in results if r[1]]
    fail_count = [r[1] for r in results if not r[1]]
    logger.debug(
        'adaptive_insert results: %s blocks, %s txs, %s succeeded, %s failed',
        len(raw_blocks), len(tx_objs), success_count, fail_count)
    return results
