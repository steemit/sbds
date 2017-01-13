# -*- coding: utf-8 -*-
import ujson as json
from itertools import chain

import click
from sqlalchemy import create_engine
from sqlalchemy import MetaData

import sbds.logging
from sbds.storages.db import Blocks
from sbds.storages.db import Transactions
from sbds.storages.db.tables import meta

from sbds.storages.db import extract_transactions_from_block
from sbds.storages.db import extract_transactions_from_blocks
from sbds.http_client import SimpleSteemAPIClient

logger = sbds.logging.getLogger(__name__)


@click.group()
@click.option('--database_url', type=str, envvar='DATABASE_URL',
              help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default')
@click.option('--echo/--no-echo', is_flag=True, default=False,
              help="Enable(default)/disable the echoing of SQL commands issued to database")
@click.pass_context
def db(ctx, database_url, echo):
    """Group of commands used to interact with the MySQL storage backend.
        Typical usage would be reading blocks in JSON format from STDIN
        and then storing those blocks in the database:

        \b
        sbds | db insert-blocks

        In the example above, the "sbds" command streams new blocks to STDOUT, which are piped to STDIN of
        the "insert-blocks" db command by default. The "database_url" was read from the "DATABASE_URL"
        ENV var, though it may optionally be provided on the command line:

        \b
        db --database_url 'dialect[+driver]://user:password@host/dbname[?key=value..]' test

    """
    engine = create_engine(database_url, echo=echo, execution_options={'stream_results': True}, encoding='utf8')
    ctx.obj = dict(engine=engine)


@db.command()
@click.pass_context
def test(ctx):
    """Test connection to database"""
    engine = ctx.obj['engine']
    result = engine.execute('SHOW TABLES').fetchall()
    click.echo('Success! Connected to database and found %s tables' % (len(result)))


@db.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    """Insert or update blocks in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, meta)

    block_storage = Blocks(engine=engine)
    map(block_storage.add, blocks)



@db.command(name='insert-transactions')
@click.argument('blocks', type=click.File('r', encoding='utf8'),  default='-')
@click.pass_context
def insert_transactions(ctx, blocks):
    """Insert or update transactions in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, meta)
    transaction_storage = Transactions(engine=engine)

    transactions_by_block = chain(map(extract_transactions_from_block, blocks))
    transactions = chain.from_iterable(transactions_by_block)
    map(transaction_storage.add, transactions)




@db.command(name='insert-blocks-and-transactions')
@click.argument('blocks', type=click.File('r', encoding='utf8'),  default='-')
@click.pass_context
def insert_blocks_and_transactions(ctx, blocks):
    """Insert or update transactions in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, meta)
    block_storage = Blocks(engine=engine)
    transaction_storage = Transactions(engine=engine)
    for block in blocks:
        block_storage.add(block)
        transaction_storage.add_many(extract_transactions_from_block(block))




@db.command(name='init')
@click.confirmation_option(prompt='Are you sure you want to create the db?')
@click.pass_context
def init_db(ctx):
    """Create any missing tables on the database"""
    engine = ctx.obj['engine']
    meta.create_all(bind=engine, checkfirst=True)


@db.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the db?')
@click.pass_context
def reset_db(ctx):
    """Drop and then create tables on the database"""
    engine = ctx.obj['engine']
    try:
        _meta = MetaData()
        _meta.reflect(bind=engine)
        _meta.drop_all(bind=engine, checkfirst=True)
    except Exception as e:
        logger.info(e)
    try:
        meta.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        logger.info(e)



@db.command(name='last-block')
@click.pass_context
def last_block(ctx):
    """Create any missing tables on the database"""
    engine = ctx.obj['engine']
    block_storage = Blocks(engine=engine)
    return click.echo(len(block_storage))


def _init_db(engine, _meta):
    """Add missing tables"""
    try:
        _meta.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        logger.debug(e)


@db.command(name='add-blocks-fast')
@click.argument('blocks', type=click.File('r', encoding='utf8'),  default='-')
@click.option('--chunksize', type=click.INT, default=1000)
@click.option('--url',
              metavar='STEEMD_HTTP_URL',
              envvar='STEEMD_HTTP_URL',
              help='Steemd HTTP server URL')
@click.pass_context
def add_blocks_fast(ctx, blocks, chunksize, url):
    """Insert or update transactions in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, meta)
    block_storage = Blocks(engine=engine)

    # attempt to add, retrying once
    total_added, skipped_blocks  = block_storage.add_many(blocks,
                                                         chunksize=chunksize,
                                                         retry_skipped=True)
    extra = dict(skipped_count=len(skipped_blocks), added=total_added)
    logger.debug('Finished initial pass', extra=extra)

    # get missing blocks, including blocks generated since command initiated
    logger.debug('Checking for missing blocks')
    rpc = SimpleSteemAPIClient(url)
    block_height = rpc.last_irreversible_block_num()
    db_last_block = len(block_storage)
    missing_block_nums = block_storage.missing(block_height=block_height)
    extra = dict(block_height=block_height,
                 db_last_block=db_last_block,
                 missing_count=len(missing_block_nums))
    logger.info('Current blocks table status', extra=extra)

    # add missing blocks
    logger.info('Adding %s missing blocks', len(missing_block_nums))
    blocks = map(rpc.get_block, missing_block_nums)
    skipped_blocks, total_added = block_storage.add_many(blocks,
                                                         chunksize=chunksize,
                                                         retry_skipped=True)


@db.command(name='add-transactions-fast')
@click.argument('blocks', type=click.File('r', encoding='utf8'),  default='-')
@click.option('--chunksize', type=click.INT, default=1000)
@click.option('--url',
              metavar='STEEMD_HTTP_URL',
              envvar='STEEMD_HTTP_URL',
              help='Steemd HTTP server URL')
@click.pass_context
def add_transactions_fast(ctx, blocks, chunksize, url):
    """Insert or update transactions in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, meta)
    transaction_storage = Transactions(engine=engine)
    transactions = extract_transactions_from_blocks(blocks)
    total_added, skipped_transactions  = transaction_storage.add_many(blocks,
                                                         chunksize=chunksize,
                                                         retry_skipped=True)
    extra = dict(skipped_count=len(skipped_transactions), added=total_added)
    logger.debug('Finished initial pass', extra=extra)