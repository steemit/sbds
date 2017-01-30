# -*- coding: utf-8 -*-


import click

from sqlalchemy import create_engine

import sbds.logging
from sbds.http_client import SimpleSteemAPIClient

from sbds.storages.db import Session
from sbds.storages.db import add_blocks
from sbds.storages.db import metadata
from sbds.storages.db.tables import Block
from sbds.utils import write_json_items

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
@click.pass_context
def insert_blocks(ctx, blocks):
    """Insert blocks in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session=Session()
    add_blocks(blocks, session)




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
