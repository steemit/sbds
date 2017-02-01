# -*- coding: utf-8 -*-
from collections import Counter
from itertools import chain

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
    try:
        block_obj, txtransactions = from_raw_block(raw_block=raw_block)
        session.add(block_obj)
        session.commit()
        session.add_all(txtransactions)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.exception(e)
        return False
    else:
        logger.debug('added block %s', block_num)
        return True


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


def add_blocks(raw_blocks, session, offset=0, report_interval=1000,
               reset_interval=100000):
    """

    :param raw_blocks: list
    :param session:
    :param offset: int
    :param report_interval: int
    :param reset_interval: int
    """
    session = new_session(session=session, Session=Session)
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
                session = new_session(session=session, Session=Session)
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
        write_json(failed_blocks, topic='failed_blocks')
        logger.info('failed_blocks: %s' % failed_blocks)

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
            session = new_session(session=session, Session=Session)
        except Exception as e:
            failed_blocks += block_nums
            logger.exception(e)
            logger.error('FAILED BLOCKS total:%s from %s to %s', block_count,
                         first_block_num, last_block_num)
            session = new_session(session=session, Session=Session)

        # Add txs
        try:
            session.bulk_save_objects(tx_objs)
            session.commit()
        except IntegrityError as e:
            failed_tx_blocks += block_nums
            session = new_session(session=session, Session=Session)
            if not is_duplicate_entry_error(e):
                logger.exception(e)
            else:
                logger.info('Duplicate entry error caught')
            logger.error('FAILED TXs FOR BLOCKS total:%s from %s to %s',
                         block_count, first_block_num, last_block_num)

        except Exception as e:
            failed_tx_blocks += block_nums
            session = new_session(session=session, Session=Session)
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


# noinspection PyPep8Naming
def bulk_add_chunkify(raw_blocks, session, Session, chunksize=100):
    """

    :param raw_blocks: list
    :param session:
    :param Session:
    :param chunksize: int
    """
    from .tables import Block
    from .tables import TxBase
    failed_blocks = []
    failed_tx_blocks = []
    try:
        for i, chunk in enumerate(partition_all(chunksize, raw_blocks), 1):
            raw_blocks_chunk = list(chunk)
            logger.info(
                    'chunk %s, block_count=%s failed__blocks: %s failed_tx_blocks:%s',
                    i, len(raw_blocks_chunk), len(failed_blocks),
                    len(failed_tx_blocks))
            block_objs = list(map(Block.from_raw_block, raw_blocks_chunk))
            tx_objs = list(chain.from_iterable(
                    map(TxBase.from_raw_block, raw_blocks_chunk)))
            logger.info('block_objs: %s tx_objs: %s', len(block_objs),
                        len(tx_objs))
            try:
                # remove existing to avoid IntegrityError

                results = session.query(Block.block_num) \
                    .filter(Block.block_num.in_(
                        [b.block_num for b in block_objs])).all()
                if results:
                    results = [r[0] for r in results]
                    logger.info('found existing blocks: %s', results)
                    new_block_objs = [b for b in block_objs if
                                      b.block_num not in results]
                    logger.info('removed %s existing objects from list',
                                len(block_objs) - len(new_block_objs))
                    block_objs = new_block_objs
                session.bulk_save_objects(block_objs)
                session.commit()
            except Exception as e:
                logger.exception(e)
                block_nums = [b['block_num'] for b in
                              map(block_info, raw_blocks_chunk)]
                logger.error('FAILED BLOCKS: %s', block_nums)
                failed_blocks += block_nums
                session = new_session(session=session, Session=Session)
            try:
                session.bulk_save_objects(tx_objs)
                session.commit()
            except Exception as e:
                logger.exception(e)
                block_nums = [b['block_num'] for b in
                              map(block_info, raw_blocks_chunk)]
                logger.error('FAILED TXs FOR BLOCKS: %s',
                             [b.block_num for b in block_objs])
                failed_tx_blocks += block_nums
                session = new_session(session=session, Session=Session)
            if i % 100 == 0:
                if len(failed_blocks) > 0:
                    write_json(failed_blocks, topic='failed_blocks')
                    failed_blocks = []
                if len(failed_tx_blocks) > 0:
                    write_json(failed_tx_blocks, topic='failed_tx_blocks')
                    failed_tx_blocks = []
    except Exception as e:
        logger.exception(e)
        if len(failed_blocks) > 0:
            write_json(failed_blocks, topic='failed_blocks')
            failed_blocks = []
        if len(failed_tx_blocks) > 0:
            write_json(failed_tx_blocks, topic='failed_tx_blocks')
            failed_tx_blocks = []
        raise e
    finally:
        if len(failed_blocks) > 0:
            write_json(failed_blocks, topic='failed_blocks')
            failed_blocks = []
        if len(failed_tx_blocks) > 0:
            write_json(failed_tx_blocks, topic='failed_tx_blocks')
            failed_tx_blocks = []
