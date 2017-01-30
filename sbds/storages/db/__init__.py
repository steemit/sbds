# -*- coding: utf-8 -*-
import toolz.itertoolz
from collections import Counter

import sbds.logging

from .tables import Session
from .tables import Base

from .tables.core import from_raw_block

from .utils import new_session
from sbds.utils import block_info

metadata = Base.metadata

logger = sbds.logging.getLogger(__name__)



def add_block(raw_block, session, info=None):
    info = info or block_info(raw_block)
    block_num = info['block_num']
    logger.debug('processing %s', info['brief'].format(**info))
    try:
        block_obj = from_raw_block(raw_block=raw_block, session=session)
        session.add(block_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.exception(e)
        return False
    else:
        logger.debug('added block %s', block_num)
        return True


def add_blocks(raw_blocks, session, offset=0, report_interval=1000, reset_interval=100000):
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
                logger.debug('failed to add block %s, wiping session', block_num)
                session = new_session(session=session, Session=Session)
                fails = ['%s_fails' % op_type for op_type in info['transactions'] ]
                counter.update(fails)
                counter['failed_blocks'] += 1
            else:
                counter.update(info['transactions'])
                counter['added_blocks'] += 1
            if i == 1:
                starting_block = block_num
            if i % report_interval == 0:
                report = dict(counter)
                report['offset']=offset
                report['report_interval'] = report_interval
                report['reset_interval'] = reset_interval
                report['failed_blocks'] = failed_blocks
                report['report_interval_start_block_num'] = starting_block
                report['report_interval_final_block_num'] = block_num
                logger.info('interval report for the last %s blocks', report_interval, extra=report)
            if i % reset_interval == 0:
                report = dict(counter)
                report['offset'] = offset
                report['report_interval'] = report_interval
                report['reset_interval'] = reset_interval
                report['reset_interval_failed_blocks'] = failed_blocks
                report['reset_interval_start_block_num'] = starting_block
                report['reset_interval_final_block_num'] = block_num
                logger.info('reset_interval report for the last %s blocks', reset_interval, extra=counter)
                logger.info('resetting counters and stats after %s blocks', reset_interval)
                counter = Counter()
                starting_block = block_num
                failed_blocks = []
    except Exception as e:
        raise e
    finally:
        logger.info('failed_blocks: %s' % failed_blocks)
        report = dict(counter)
        report['offset'] = offset
        report['report_interval'] = report_interval
        report['reset_interval'] = reset_interval
        report['failed_blocks'] = failed_blocks
        report['report_interval_start_block_num'] = starting_block
        report['report_interval_final_block_num'] = block_num
        logger.info('final report before quit',  extra=report)