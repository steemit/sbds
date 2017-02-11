# -*- coding: utf-8 -*-

import json
import click
from sqlalchemy import create_engine

import sbds.logging
from sbds.storages.db import Session
from sbds.storages.db import add_blocks
from sbds.storages.db import bulk_add
# from sbds.storages.db import metadata
from sbds.storages.db import Base
from sbds.storages.db.tables import Block
from sbds.utils import chunkify

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
        db --database_url 'dialect[+driver]://user:password@host/dbname[?key=value..]' tests

    """
    if 'sqlite' in database_url.split(':')[0]:
        engine = create_engine(database_url)
    else:
        engine = create_engine(database_url,
                               server_side_cursors=True,
                               encoding='utf8')
    ctx.obj = dict(engine=engine,
                   base=Base,
                   metadata=Base.metadata,
                   Session=Session)


@db.command()
@click.pass_context
def test(ctx):
    """Test connection to database"""
    engine = ctx.obj['engine']
    result = engine.execute('SHOW TABLES').fetchall()
    click.echo(
            'Success! Connected to database and found %s tables' % (
                len(result)))


@db.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    """Insert blocks in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session = Session()
    add_blocks(blocks, session)


@db.command(name='bulk-add')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.option('--chunksize', type=click.INT, default=1000)
@click.pass_context
def bulk_add_blocks(ctx, blocks, chunksize):
    """Insert blocks in the database, accepts "-" for STDIN (default)"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session = Session()
    click.echo("SQL: 'SET SESSION innodb_lock_wait_timeout=150'", err=True)
    session.execute('SET SESSION innodb_lock_wait_timeout=150')
    try:
        for chunk in chunkify(blocks, chunksize):
            bulk_add(chunk, session)
    except Exception as e:
        raise e
    finally:
        session.close_all()


@db.command(name='init')
@click.pass_context
def init_db_tables(ctx):
    """Create any missing tables on the database"""
    engine = ctx.obj['engine']
    metadata = ctx.obj['metadata']
    metadata.create_all(bind=engine, checkfirst=True)


@db.command(name='reset')
@click.confirmation_option(
        prompt='Are you sure you want to drop and then create the db?')
@click.pass_context
def reset_db_tables(ctx):
    """Drop and then create tables on the database"""
    engine = ctx.obj['engine']
    metadata = ctx.obj['metadata']

    # use unadulterated MetaData to avoid errors due to ORM classes
    # being inconsistent with existing tables
    from sqlalchemy import MetaData
    _metadata = MetaData()
    _metadata.reflect(bind=engine)
    _metadata.drop_all(bind=engine)

    # use ORM clases to define tables to create
    metadata.create_all(bind=engine, checkfirst=True)
    ctx.exit(code=0)


@db.command(name='last-block')
@click.pass_context
def last_block(ctx):
    """Create any missing tables on the database"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session = Session()
    click.echo(Block.highest_block(session))


@db.command(name='find-missing-blocks')
@click.pass_context
def find_missing_blocks(ctx):
    """JSON array of block_nums from missing blocks"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session = Session()
    click.echo(json.dumps(Block.find_missing(session)))


@db.command(name='add-missing-posts-and-comments')
@click.pass_context
def add_missing_posts_and_comments(ctx):
    """add missing posts and comments from txcomments"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    from sbds.storages.db.tables import PostAndComment
    PostAndComment.add_missing(Session)


@db.command(name='find-missing-posts-and-comments')
@click.pass_context
def find_missing_posts_and_comments(ctx):
    """JSON array of block_nums from missing post and comment blocks"""
    engine = ctx.obj['engine']
    Session.configure(bind=engine)
    session = Session()
    from sbds.storages.db.tables import PostAndComment
    block_nums = PostAndComment.find_missing_block_nums(session)
    click.echo(json.dumps(block_nums))
