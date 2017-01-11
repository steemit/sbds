# -*- coding: utf-8 -*-
import ujson as json
from itertools import chain

import click
from sqlalchemy import create_engine

import sbds.logging
from sbds.storages.db import Blocks
from sbds.storages.db import Transactions
from sbds.storages.db.tables import meta

from sbds.storages.db import extract_transaction_from_block
from sbds.storages.db import extract_transaction_from_prepared_block

logger = sbds.logging.getLogger(__name__)


@click.group()
@click.option('--database_url', type=str, envvar='DATABASE_URL',
              default='sqlite:///local.db',
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
    engine = create_engine(database_url, echo=echo, execution_options={'stream_results': True})
    ctx.obj = dict(engine=engine)


@db.command()
@click.pass_context
def test(ctx):
    "Test connection to database"
    engine = ctx.obj['engine']
    result = engine.execute('SHOW TABLES').fetchall()
    click.echo('Success! Connected to database and found %s tables' % (len(result)))


@db.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    '''Insert or update blocks in the database, accepts "-" for STDIN (default)'''
    engine = ctx.obj['engine']
    _init_db(engine, meta)

    block_storage = Blocks(engine=engine)
    added_count, skipped_blocks = block_storage.add_many(blocks)
    extra = dict(added_count=added_count, skipped_count=len(skipped_blocks))
    logger.info('Completed adding blocks', extra=extra)
    if len(skipped_blocks) is 0:
        return

    # Added skipped blocks and transactions
    logger.info('Adding skipped blocks and transactions')
    transaction_storage = Transactions(engine=engine)
    for block in skipped_blocks:
        block_storage.add(block, prepared=True)
        for transaction in extract_transaction_from_prepared_block(block):
            transaction_storage.add(transaction, prepared=True)


@db.command(name='insert-transactions')
@click.argument('blocks', type=click.File('r'), default='-')
@click.pass_context
def insert_transactions(ctx, blocks):
    '''Insert or update transactions in the database, accepts "-" for STDIN (default)'''
    engine = ctx.obj['engine']
    _init_db(engine, meta)

    transaction_storage = Transactions(engine=engine)
    transactions_by_block = chain(map(extract_transaction_from_block, blocks))
    transactions = chain.from_iterable(transactions_by_block)
    added_count, skipped_transactions = transaction_storage.add_many(transactions)

    extra = dict(added_count=added_count, skipped_count=len(skipped_transactions))
    logger.info('Completed adding transactions', extra=extra)
    if len(skipped_transactions) is 0:
        return
    logger.info('Adding skipped transactions')
    for transaction in skipped_transactions:
        transaction_storage.add(transaction, prepared=True)



@db.command(name='init')
@click.confirmation_option(prompt='Are you sure you want to create the db?')
@click.pass_context
def init_db(ctx):
    "Create any missing tables on the database"
    engine = ctx.obj['engine']
    meta.create_all(bind=engine, checkfirst=True)


@db.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the db?')
@click.pass_context
def reset_db(ctx):
    "Drop and then create tables on the database"
    engine = ctx.obj['engine']
    meta.drop_all(bind=engine, checkfirst=True)
    meta.create_all(bind=engine)

@db.command(name='last-block')
@click.pass_context
def last_block(ctx):
    "Create any missing tables on the database"
    engine = ctx.obj['engine']
    block_storage = Blocks(engine=engine)
    return click.echo(len(block_storage))

def _init_db(engine, meta, echo=click.echo):
    '''Add missing tables'''
    try:
        meta.create_all(bind=engine, checkfirst=True)
    except:
        pass