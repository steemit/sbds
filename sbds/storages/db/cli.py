# -*- coding: utf-8 -*-

from collections import Counter
import click

from sqlalchemy import create_engine


import sbds.logging
from sbds.http_client import SimpleSteemAPIClient

from sbds.storages.db import Session
from sbds.storages.db import add_block
from sbds.storages.db import metadata
from sbds.storages.db.tables import Block
from sbds.utils import write_json_items
from .utils import new_session
from sbds.utils import block_info

logger = sbds.logging.getLogger(__name__)


@click.group()
@click.option('--database_url', type=str, envvar='DATABASE_URL',
              help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default')
@click.pass_context
def db(ctx, database_url):
    """Group of commands used to interact with the SQL storage backend.
        Typical usage would be reading blocks in JSON format from STDIN
        and then storing those blocks in the database:

        \b
        sbds | db insert-blocks

        In the example above, the "sbds" command streams new blocks to STDOUT, which are piped to STDIN of
        the "db insert-blocks" command by default. The "database_url" was read from the "DATABASE_URL"
        ENV var, though it may optionally be provided on the command line:

        \b
        db --database_url 'dialect[+driver]://user:password@host/dbname[?key=value..]' test

    """
    engine = create_engine(database_url, server_side_cursors=True, encoding='utf8')

    ctx.obj = dict(engine=engine, metadata=metadata, Session=Session)


@db.command()
@click.pass_context
def test(ctx):
    """Test connection to database"""
    engine = ctx.obj['engine']
    result = engine.execute('SHOW TABLES').fetchall()
    click.echo('Success! Connected to database and found %s tables' % (len(result)))


@db.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.option('--report_interval', type=click.INT, default=100)
@click.option('--reset_interval', type=click.INT, default=100000)
@click.pass_context
def insert_blocks(ctx, blocks, report_interval, reset_interval):
    """Insert blocks in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session=Session()
    counter = Counter()
    failed_blocks = []
    starting_block = None
    try:
        for i, raw_block in enumerate(blocks, 1):
            info = block_info(raw_block)
            block_num = info['block_num']
            counter['attempted_blocks'] += 1
            result = add_block(raw_block, session, info=info)
            if not result:
                logger.error('BLOCK %s WAS NOT ADDED', block_num)
                failed_blocks.append(block_num)
                logger.debug('failed to add block %s, wiping session', block_num)
                session = new_session(session=session, Session=Session)
                fails = ['%s_fails' % op_type for op_type in info['transactions']]
                counter.update(fails)
                counter['failed_blocks'] += 1
            else:
                counter.update(info['transactions'])
                counter['added_blocks'] += 1
            if i == 1:
                starting_block = block_num
            if i % report_interval == 0:
                report = dict(counter)
                report['report_interval'] = report_interval
                report['reset_interval'] = reset_interval
                report['failed_blocks'] = failed_blocks
                report['report_interval_start_block_num'] = starting_block
                report['report_interval_final_block_num'] = block_num
                logger.info('interval report for the last %s blocks', report_interval, extra=report)
            if i % reset_interval == 0:
                report = dict(counter)
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
        logger.exception(e)
        raise e
    finally:
        logger.info('failed_blocks: %s' % failed_blocks)
        report = dict(counter)
        report['report_interval'] = report_interval
        report['reset_interval'] = reset_interval
        report['failed_blocks'] = failed_blocks
        report['report_interval_start_block_num'] = starting_block
        report['report_interval_final_block_num'] = block_num
        logger.info('final report before quit', extra=report)




@db.command(name='init')
@click.confirmation_option(prompt='Are you sure you want to create the db?')
@click.pass_context
def init_db_tables(ctx):
    """Create any missing tables on the database"""
    engine = ctx.obj['engine']
    _metadata = ctx.obj['metadata']
    _metadata.create_all(bind=engine, checkfirst=True)


@db.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the db?')
@click.pass_context
def reset_db_tables(ctx):
    """Drop and then create tables on the database"""
    engine = ctx.obj['engine']
    from sqlalchemy import MetaData
    try:
        _meta = MetaData()
        _meta.reflect(bind=engine)
        _meta.drop_all(bind=engine, checkfirst=True)
    except Exception as e:
        logger.info(e)
    try:
        metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        logger.info(e)


@db.command(name='last-block')
@click.pass_context
def last_block(ctx):
    """Create any missing tables on the database"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session = Session()
    click.echo(Block.highest_block(session))
