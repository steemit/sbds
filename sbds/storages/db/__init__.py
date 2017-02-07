# -*- coding: utf-8 -*-
from collections import Counter
from itertools import chain
from contextlib import contextmanager
from collections import namedtuple

import toolz.itertoolz
from sqlalchemy.exc import IntegrityError
from toolz.itertoolz import partition_all

import sbds.logging
from sbds.utils import block_info
from sbds.utils import write_json
from .tables import Base
from .tables import Session
from .tables.core import from_raw_block
from .utils import is_duplicate_entry_error
from .utils import new_session

metadata = Base.metadata

logger = sbds.logging.getLogger(__name__)

LogTuple = namedtuple('LogTuple', ['cls','block_num', 'transaction_num','operation_num', 'error'])


def merge_insert(objects, session, load=True):
    for object in objects:
        try:
            session.merge(object, load=load)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        else:
            return True

def safe_insert(obj, session):
    rollback = False
    json_log = False
    try:
        logger.debug('attempting safe_insert %s', obj)
        session.add(obj)
        session.commit()
    except IntegrityError as e:
        rollback = True
        if not is_duplicate_entry_error(e):
            logger.exception(e)
        else:
            logger.info('Duplicate entry error caught')
    except Exception as e:
        rollback = True
        json_log = True
        logger.exception(e)
    else:
        logger.debug('safe_insert %s sucess', obj)
    finally:
        if rollback:
            session.rollback()
        if json_log:
            name = obj.__class__.__name__
            lt = LogTuple(cls=name,
                          block_num=getattr(object, 'block_num', None),
                          transaction_num=getattr(object, 'transaction_num', None),
                          operation_num=getattr(object, 'operation_num', None),
                          error=e)
            write_json([lt._asdict()],topic='failed_%s' % name)

        return not rollback


def safe_insert_many(objects, session):
    rollback = False
    json_log = False
    outer_error = None
    e = None
    try:
        session.add_all(objects)
        session.commit()
    except IntegrityError as e:
        rollback = True
        if not is_duplicate_entry_error(e):
            logger.exception(e)
        else:
            logger.info('Duplicate entry error caught')
    except Exception as e:
        rollback = True
        json_log = True
        logger.exception(e)
        outer_error = e
    finally:
        if rollback:
            session.rollback()
        if json_log:
            log_tuples = []
            for object in objects:
                name = object.__class__.__name__

                lt = LogTuple(cls=name,
                          block_num=getattr(object, 'block_num', None),
                          transaction_num=getattr(object, 'transaction_num', None),
                          operation_num=getattr(object, 'operation_num', None),
                          error=outer_error)
                log_tuples.append(lt._asdict())
            write_json(log_tuples, topic='failed_inserts')

        return not rollback

def adaptive_insert(objects, session):
    if safe_insert_many(objects, session):
        logger.debug('attepmting safe_insert_many')
        return True

    logger.debug('safe_insert_many failed')
    try:
        logger.debug('attempting merge_insert')
        merge_insert(objects, session)
        logger.debug('merge_insert success')
        return True
    except Exception as e:
        logger.debug('merge_insert failed')
        logger.error(e)
        logger.debug('attempting individual safe_insert')
        return [safe_insert(object, session) for object in objects]


def add_block(raw_block, session, info=None):
    """

    :param raw_block: str
    :param session:
    :param info: dict
    :return: boolean
    """
    info = info or block_info(raw_block)
    block_num = info['block_num']
    logger.debug('processing %s', info['brief'].format(**info))
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
               offset=0,
               report_interval=1000,
               reset_interval=100000):
    """

    :param raw_blocks: list
    :param session:
    :param offset: int
    :param report_interval: int
    :param reset_interval: int
    """
    if offset != 0:
        raw_blocks = toolz.itertoolz.drop(offset, raw_blocks)
    counter = Counter()
    failed_blocks = []
    starting_block = None
    try:
        for i, raw_block in enumerate(raw_blocks, 1):
            info = block_info(raw_block)
            block_num = info['block_num']
            counter['attempted_blocks'] += 1
            result = add_block(raw_block, session, info=info)
            if not result:
                logger.error('BLOCK %s WAS NOT ADDED', block_num)
                failed_blocks.append(block_num)
                logger.debug('failed to add block %s, wiping session',
                             block_num)
                session = new_session(session=session, session_factory=Session)
                fails = ['%s_fails' % op_type for op_type in
                         info['transactions']]
                counter.update(fails)
                counter['failed_blocks'] += 1
            else:
                counter.update(info['transactions'])
                counter['added_blocks'] += 1
            if i == 1:
                starting_block = block_num
            if i % report_interval == 0:
                report = dict(counter)
                report['offset'] = offset
                report['report_interval'] = report_interval
                report['reset_interval'] = reset_interval
                report['failed_blocks'] = failed_blocks
                report['report_interval_start_block_num'] = starting_block
                report['report_interval_final_block_num'] = block_num
                logger.info('interval report for the last %s blocks',
                            report_interval, extra=report)
            if i % reset_interval == 0:
                report = dict(counter)
                report['offset'] = offset
                report['report_interval'] = report_interval
                report['reset_interval'] = reset_interval
                report['reset_interval_failed_blocks'] = failed_blocks
                report['reset_interval_start_block_num'] = starting_block
                report['reset_interval_final_block_num'] = block_num
                logger.info('reset_interval report for the last %s blocks',
                            reset_interval, extra=counter)
                logger.info('resetting counters and stats after %s blocks',
                            reset_interval)
                counter = Counter()
                starting_block = block_num
                failed_blocks = []
    except Exception as e:
        raise e
    finally:
        report = dict(counter)
        report['offset'] = offset
        report['report_interval'] = report_interval
        report['reset_interval'] = reset_interval
        report['failed_blocks'] = failed_blocks
        report['report_interval_start_block_num'] = starting_block
        report['report_interval_final_block_num'] = block_num
        logger.info('final report before quit', extra=report)


# noinspection PyPep8Naming
def bulk_add(raw_blocks, session, Session, retry=True):
    """

    :param raw_blocks: list
    :param session:
    :param Session:
    :param retry: bool
    """
    from .tables import Block
    from .tables import TxBase
    failed_blocks = []
    failed_tx_blocks = []
    try:
        raw_blocks_chunk = list(raw_blocks)
        block_nums = [b['block_num'] for b in map(block_info, raw_blocks_chunk)]
        block_count = len(raw_blocks_chunk)
        first_block_num = block_nums[0]
        last_block_num = block_nums[-1]
        logger.info(
                'chunk_begin: %s chunk_end:% block_count=%s failed__blocks: %s failed_tx_blocks:%s',
                first_block_num,
                last_block_num,
                block_count,
                len(failed_blocks),
                len(failed_tx_blocks))
        block_objs = list(map(Block.from_raw_block, raw_blocks_chunk))
        tx_objs = list(
                chain.from_iterable(
                        map(TxBase.from_raw_block, raw_blocks_chunk)))
        logger.info('block_objs: %s tx_objs: %s', len(block_objs), len(tx_objs))

        # Add blocks
        try:
            # remove existing to avoid IntegrityError
            block_objs = filter_existing_blocks(block_objs, session)
            session.bulk_save_objects(block_objs)
            session.commit()
        except IntegrityError as e:
            failed_blocks += block_nums
            if not is_duplicate_entry_error(e):
                logger.exception(e)
            else:
                logger.info('Duplicate entry error caught')
            logger.error('FAILED BLOCKS total:%s from %s to %s', block_count,
                         first_block_num, last_block_num)
            session = new_session(session=session, session_factory=Session)
        except Exception as e:
            failed_blocks += block_nums
            logger.exception(e)
            logger.error('FAILED BLOCKS total:%s from %s to %s', block_count,
                         first_block_num, last_block_num)
            session = new_session(session=session, session_factory=Session)

        # Add txs
        try:
            session.bulk_save_objects(tx_objs)
            session.commit()
        except IntegrityError as e:
            failed_tx_blocks += block_nums
            session = new_session(session=session, session_factory=Session)
            if not is_duplicate_entry_error(e):
                logger.exception(e)
            else:
                logger.info('Duplicate entry error caught')
            logger.error('FAILED TXs FOR BLOCKS total:%s from %s to %s',
                         block_count, first_block_num, last_block_num)

        except Exception as e:
            failed_tx_blocks += block_nums
            session = new_session(session=session, session_factory=Session)
            logger.exception(e)
            logger.error('FAILED TXs FOR BLOCKS total:%s from %s to %s',
                         block_count, first_block_num, last_block_num)


    # loop error handlers
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        if len(failed_blocks) > 0:
            write_json(failed_blocks, topic='failed_blocks')
        if len(failed_tx_blocks) > 0:
            write_json(failed_tx_blocks, topic='failed_tx_blocks')
        logger.info(
                'chunk_begin: %s chunk_end:% block_count=%s failed__blocks: %s failed_tx_blocks:%s',
                first_block_num,
                last_block_num,
                len(raw_blocks_chunk),
                len(failed_blocks),
                len(failed_tx_blocks))
