# -*- coding: utf-8 -*-
from itertools import chain
from itertools import zip_longest
from typing import Dict, Tuple, List, Union

import toolz.itertoolz
from sqlalchemy.orm.util import object_state

from sbds.sbds_logging import generate_fail_log_from_obj
from sbds.sbds_logging import getLogger

from sbds.utils import block_info

from .tables.core import from_raw_block
from .tables.core import extract_transactions_from_block
from .utils import is_duplicate_entry_error
from .utils import session_scope

logger = getLogger(__name__)


# pylint: disable=bare-except,too-many-branches,too-many-arguments, unused-argument
def safe_merge_insert(objects, session, load=True, **kwargs):
    """
    Merge objects into session and commit session.

    Args:
        objects (List[TxBase, Block]):
        session (sqlalchemy.orm.session.Session):
        load (bool):
        **kwargs (dict):

    Returns:
        bool:
    """
    # pylint: disable=bare-except
    try:
        with session_scope(session, _raise_all=True) as s:
            for obj in objects:
                s.merge(obj, load=load)
    except:
        return False
    else:
        return True


def safe_insert(obj, session, **kwargs):
    """
    Add single object to session and commit session.

    Args:
        obj (Union[TxBase,Block]):
        session (sqlalchemy.orm.session.Session):
        **kwargs (dict):

    Returns:
        bool:
    """
    with session_scope(session, **kwargs) as s:
        s.add(obj)
    result = getattr(object_state(obj), 'persistent', False)
    return result


def safe_insert_many(objects, session, **kwargs):
    """
    Add all objects to session and commit session.

    Args:
        objects (List[TxBase, Block]):
        session (sqlalchemy.orm.session.Session):
        **kwargs (dict):

    Returns:
        bool:
    """
    # noinspection PyBroadException
    try:
        with session_scope(session, _raise_all=True) as s:
            s.add_all(objects)
    except:
        return False
    else:
        return True


def safe_bulk_save(objects, session, **kwargs):
    """
    Bulk save objects.

    Args:
        objects (List[TxBase, Block]):
        session (sqlalchemy.orm.session.Session):
        **kwargs (dict):

    Returns:
        bool:
    """
    # noinspection PyBroadException
    try:
        with session_scope(session, _raise_all=True) as s:
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
    """
    Add Blocks and Txs using succesion of different insert methods.

    Args:
        objects (List[TxBase, Block]):
        session (sqlalchemy.orm.session.Session):
        bulk (bool):
        insert_many (bool):
        merge_insert (bool):
        insert (bool):
        **kwargs (dict):

    Returns:
        results (list[bool]):

    """
    # pylint: disable=too-many-return-statements
    if not objects:
        logger.debug('adaptive_insert called with empty objects list')
        return True

    results = list(zip_longest(objects, list(), fillvalue=False))

    if bulk:
        logger.debug('attempting bulk_save')
        if safe_bulk_save(objects, session, **kwargs):
            logger.debug('bulk_save success')
            return list(zip_longest(objects, list(), fillvalue=True))
        else:
            fail_reason = session.info.get('err', '')
            logger.info('bulk_save failed %s', fail_reason)
            results = list(zip_longest(objects, list(), fillvalue=False))

    if insert_many:
        logger.debug('attempting safe_insert_many')
        if safe_insert_many(objects, session, **kwargs):
            logger.debug('safe_insert_many success')
            return list(zip_longest(objects, list(), fillvalue=True))
        else:
            fail_reason = session.info.get('err', '')
            logger.info('safe_insert_many failed %s', fail_reason)
            results = list(zip_longest(objects, list(), fillvalue=False))

    if merge_insert:
        logger.debug('attempting safe_merge_insert')
        if safe_merge_insert(objects, session, **kwargs):
            logger.debug('safe_merge_insert success')
            return list(zip_longest(objects, list(), fillvalue=True))
        else:
            fail_reason = session.info.get('err', '')
            logger.info('safe_merge_insert failed %s', fail_reason)
            results = list(zip_longest(objects, list(), fillvalue=False))

    if insert:
        logger.debug('attempting individual safe_insert')
        sub_results = [safe_insert(obj, session, **kwargs) for obj in objects]
        results = list(zip_longest(objects, sub_results))
        if all(r[1] for r in results):
            logger.debug('individual safe_insert success')
            return results

        logger.info(
            'individual safe_insert results: failed to insert %s of %s objects',
            list(r[1] for r in results).count(False), len(objects))

    # log failed objects
    for obj, result in zip(objects, results):
        if not result:
            generate_fail_log_from_obj(logger, obj)

    logger.info('adaptive_insert failed to persist %s out of %s objects',
                list(r[1] for r in results).count(False), len(objects))
    return results


def add_block(raw_block, session, insert=False, **kwargs):
    """
    Add a Block and its Txs.

    Args:
        raw_block (Union[Dict[str, str],str,bytes]):
        session (sqlalchemy.orm.session.Session):
        insert (bool):
        **kwargs (dict):

    Returns:
        results (List[bool]):
   """
    block_obj, txtransactions = from_raw_block(raw_block)
    results = adaptive_insert(
        list([block_obj, *txtransactions]), session, insert=insert, **kwargs)
    return results


def filter_existing_blocks(block_objects, session):
    """
    Remove existing Blocks from a list of Blocks.

    Args:
        block_objects (List[Block]):
        session (sqlalchemy.orm.session.Session):

    Returns:
        block_objects (List[Block]):
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


def add_blocks(raw_blocks, session, offset=0, **kwargs):
    """
    Add Blocks and Txs.

    Args:
        raw_blocks (Union[dict,str,bytes]):
        session (sqlalchemy.orm.session.Session):
        offset (int):

    Returns:
        results (List[bool]):
    """
    if offset != 0:
        raw_blocks = toolz.itertoolz.drop(offset, raw_blocks)
    results = []
    for raw_block in raw_blocks:
        results.extend(add_block(raw_block, session, **kwargs))
    return results


def bulk_add(raw_blocks, session):
    """
    Add Blocks and Txs as quickly as possible.

    Args:
        raw_blocks (Union[Dict[str, str],str,bytes]):
        session (sqlalchemy.orm.session.Session):

    Returns:
        results (List[bool]):
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
    success_count = list(r[1] for r in results).count(True)
    fail_count = list(r[1] for r in results).count(False)
    logger.info(
        'adaptive_insert results: %s blocks, %s txs, %s succeeded, %s failed',
        len(raw_blocks), len(tx_objs), success_count, fail_count)
    return results



def bulk_add_transactions(raw_blocks, session, include_types=None, exclude_types=None):
    """
    Add Blocks and Txs as quickly as possible.

    Args:
        raw_blocks (Union[Dict[str, str],str,bytes]):
        session (sqlalchemy.orm.session.Session):

    Returns:
        results (List[bool]):
    """
    from .tables import Block
    from .tables import TxBase

    raw_blocks_chunk = list(raw_blocks)
    tx_objs = list(
            chain.from_iterable(map(TxBase.from_raw_block, raw_blocks_chunk)))
    logger.info('processing %s tx_objs before filtering', len(tx_objs))
    if include_types:
        includes = set(include_types)
        logger.debug('including only %s operations', includes)
        filtered_txs = list(filter(lambda x: x.operation_type in includes , tx_objs))
    elif exclude_types:
        excludes = set(exclude_types)
        logger.info('excluding %s operations', excludes)
        filtered_txs = list(filter(lambda x: x.operation_type not in excludes, tx_objs))
    else:
        filtered_txs = tx_objs
    logger.info('%s operations after filtering', len(filtered_txs))

    # add blocks (only if we havent removed them all)
    objs_to_add = filtered_txs
    results = adaptive_insert(objs_to_add, session, bulk=True)
    success_count = list(r[1] for r in results).count(True)
    fail_count = list(r[1] for r in results).count(False)
    logger.info(
        'adaptive_insert results: %s txs, %s succeeded, %s failed',
        len(objs_to_add), success_count, fail_count)
    return results