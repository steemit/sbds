# -*- coding: utf-8 -*-
import json

import click
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

import sbds.logging
from sbds.storages.mysql import Blocks
from sbds.storages.mysql.tables import meta

logger = sbds.logging.getLogger(__name__)


@click.group()
@click.option('--database_url', type=str, envvar='DATABASE_URL',
              help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default')
@click.option('--echo/--no-echo', is_flag=True, default=True,
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


@db.command()
@click.argument('sql', type=str)
@click.pass_context
def query(ctx, sql):
    "Execute SQL on the database"
    engine = ctx.obj['engine']
    click.echo(engine.execute(sql).fetchall())

# help='File like object to read blocks from, accepts "-" for STDIN (default)'
@db.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    'Insert or update blocks in the database, accepts "-" for STDIN (default)'
    engine = ctx.obj['engine']
    block_storage = Blocks(engine=engine)
    missing = find_missing_tables(engine, meta.tables)
    if missing:
        meta.create_all(bind=engine, checkfirst=True)
    for block in blocks:
        data = json.loads(block)
        try:
            block_storage[data['block_num']] = block
        except IntegrityError as e:
            logger.info(e)


@db.command(name='insert-transactions')
@click.argument('blocks', type=click.File('r'), default='-')
@click.pass_context
def insert_transactions(ctx, transactions):
    'Insert or update transactions in the database, accepts "-" for STDIN (default)'
    engine = ctx.obj['engine']
    transaction_storage = Transactions(engine=engine)
    for block in transactions:
        data = json.loads(block)
        try:
            transaction_storage[data['block_num']] = block
        except Exception as e:
            logger.error(e)


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


def add_all(database_url, blocks):



def find_missing_tables(engine, correct_tables):
    meta = MetaData()
    meta.reflect(bind=engine)
    missing = []
    for table in correct_tables.values():
        try:
            table.exists(bind=engine)
        except Exception as e:
            logger.info('%s table missing from %s', table, engine)
            missing.append(table)
    return missing