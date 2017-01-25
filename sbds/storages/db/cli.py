# -*- coding: utf-8 -*-
import json
import os
from itertools import chain
from functools import partial

import click
from sqlalchemy import create_engine
from sqlalchemy import MetaData

import sbds.logging
from sbds.storages.db import Blocks

from sbds.storages.db import Operations
from sbds.storages.db import Transactions
from sbds.storages.db.tables import metadata

from sbds.storages.db import extract_transactions_from_block
from sbds.storages.db import extract_transactions_from_blocks
from sbds.storages.db import extract_operations_from_blocks

from sbds.http_client import SimpleSteemAPIClient

from sbds.utils import chunkify
from sbds.utils import write_json_items

logger = sbds.logging.getLogger(__name__)


@click.group()
@click.option('--database_url', type=str, envvar='DATABASE_URL',
              help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default')
@click.option('--echo/--no-echo', is_flag=True, default=False,
              help="Enable(default)/disable the echoing of SQL commands issued to database")
@click.pass_context
def db(ctx, database_url, echo):
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
    ctx.obj = dict(engine=engine)


@db.command()
@click.pass_context
def test(ctx):
    """Test connection to database"""
    engine = ctx.obj['engine']
    result = engine.execute('SHOW TABLES').fetchall()
    click.echo('Success! Connected to database and found %s tables' % (len(result)))


@db.command(name='insert-all')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_all(ctx, blocks):
    """Insert block data into all database tables, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, metadata)

    block_storage = Blocks(engine=engine)
    operation_storage = Operations(engine=engine)
    for block in blocks:
        try:
            block_storage.add(block)
        except Exception as e:
            logger.exception(e)
        try:
            operation_storage.add_from_block(block)
        except Exception as e:
            logger.exception(e)

@db.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    """Insert or update blocks in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, metadata)

    block_storage = Blocks(engine=engine)
    for block in blocks:
        block_storage.add(block)
        click.echo(block)


@db.command(name='init')
@click.confirmation_option(prompt='Are you sure you want to create the db?')
@click.pass_context
def init_db_tables(ctx):
    """Create any missing tables on the database"""
    engine = ctx.obj['engine']
    metadata.create_all(bind=engine, checkfirst=True)


@db.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the db?')
@click.pass_context
def reset_db_tables(ctx):
    """Drop and then create tables on the database"""
    engine = ctx.obj['engine']
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
@click.option('--raise-on-error/--no-raise-on-error', is_flag=True, default=False,
              help="Raise errors")
@click.pass_context
def add_blocks_fast(ctx, blocks, chunksize, url, raise_on_error):
    """Quickly Insert  blocks in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, metadata)
    block_storage = Blocks(engine=engine)

    # attempt to add, retrying once
    total_added, skipped_blocks  = block_storage.add_many(blocks,
                                                         chunksize=chunksize,
                                                         retry_skipped=True,
                                                          raise_on_error=raise_on_error)
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
@click.option('--raise-on-error/--no-raise-on-error', is_flag=True, default=False,
              help="Raise errors")
@click.pass_context
def add_transactions_fast(ctx, blocks, chunksize, url, raise_on_error):
    """Insert or update transactions in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, metadata)
    transaction_storage = Transactions(engine=engine)
    transactions = extract_transactions_from_blocks(blocks)
    total_added, skipped_transactions  = transaction_storage.add_many(transactions,
                                                         chunksize=chunksize,
                                                         retry_skipped=True,
                                                         raise_on_error=raise_on_error)
    extra = dict(skipped_count=len(skipped_transactions), added=total_added)
    logger.debug('Finished initial pass', extra=extra)



@db.command(name='add-operations-fast')
@click.argument('blocks', type=click.File('r', encoding='utf8'),  default='-')
@click.option('--chunksize', type=click.INT, default=1000)
@click.option('--raise-on-error/--no-raise-on-error', is_flag=True, default=False,
              help="Raise errors")
@click.option('--skipped_operations_file',
                default='skipped_operations.json',
                help='filename to write skipped operations',
                type=click.Path(dir_okay=False, file_okay=True, resolve_path=True))
@click.pass_context
def add_operations_fast(ctx, blocks, chunksize, raise_on_error, skipped_operations_file):
    """Quickly Insert operations in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    _init_db(engine, metadata)
    operation_storage = Operations(engine=engine)
    operations = extract_operations_from_blocks(blocks)
    total_added = 0
    skipped_operations = 0
    operations_read = 0
    write_json = partial(write_json_items, skipped_operations_file)
    for chunk_num,chunk in enumerate(chunkify(operations, chunksize=chunksize),1):
        click.echo('adding chunk %s (%s items)' % (chunk_num, len(chunk)), err=True)
        chunk_total_added, chunk_skipped_operations  = operation_storage.add_many(chunk,
                                                         chunksize=chunksize,
                                                         retry_skipped=True,
                                                         raise_on_error=raise_on_error)
        # logging info
        total_added += chunk_total_added
        operations_read += len(chunk)
        skipped_operations += len(chunk_skipped_operations)
        write_json(chunk_skipped_operations)
        extra = dict(chunk_num=chunk_num,
                     chunk_added=chunk_total_added,
                     total_added=total_added,
                     operations_read=operations_read,
                     skipped_operations=skipped_operations)

        logger.info('Chunk %s processed', chunk_num, extra=extra)
        [h.flush() for h in logger.handlers]
    extra = dict(skipped_count=skipped_operations,
                     added=total_added)
    logger.debug('Finished initial pass', extra=extra)

