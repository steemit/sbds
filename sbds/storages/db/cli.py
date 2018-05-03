# -*- coding: utf-8 -*-
import asyncio
import json

import click

import structlog
from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session
from sbds.storages.db.tables import init_tables
from sbds.storages.db.tables import reset_tables
from sbds.storages.db.tables import test_connection


from sbds.storages.db.utils import isolated_engine_config
from sbds.utils import chunkify

logger = structlog.get_logger(__name__)


@click.group(name='db', short_help='Interact with an SQL storage backend')
@click.option(
    '--database_url',
    type=str,
    envvar='DATABASE_URL',
    required=True,
    help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default'
)
@click.option('--echo', is_flag=True)
@click.pass_context
def cli(ctx, database_url, echo):
    """Interact with an SQL storage backend
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
    with isolated_engine_config(database_url, echo=echo) as engine_config:
        ctx.obj = dict(
            database_url=database_url,
            url=engine_config.url,
            engine_kwargs=engine_config.engine_kwargs,
            engine=engine_config.engine,
            base=Base,
            metadata=Base.metadata,
            Session=Session)


@cli.command()
@click.pass_context
def test(ctx):
    """Test connection to database"""
    database_url = ctx.obj['database_url']
    url, table_count = test_connection(database_url)
    if url:
        click.echo('Success! Connected using %s, found %s tables' %
                   (url.__repr__(), table_count))
    else:
        click.echo('Failed to connect: %s' % url)
        ctx.exit(code=127)


@cli.command(name='init')
@click.pass_context
def init_db_tables(ctx):
    """Create any missing tables on the database"""
    database_url = ctx.obj['database_url']
    metadata = ctx.obj['metadata']
    click.echo(f'Success! Initialized db at {database_url}')
    init_tables(database_url, metadata)


@cli.command(name='reset')
@click.pass_context
def reset_db_tables(ctx):
    """Drop and then create tables on the database"""
    database_url = ctx.obj['database_url']
    metadata = ctx.obj['metadata']
    url, table_count = test_connection(database_url)
    if url:
        click.echo(f'Connected to {url.__repr__()}')
        if click.confirm(
                f'Are you sure you want to drop and then create all db tables?', abort=True):
            reset_tables(database_url, metadata)
            click.echo(f'Success! Initialized db at {url.__repr__()}')


@cli.command(name='raw-sql')
@click.argument('sql')
@click.pass_context
def raw_sql(ctx, sql):
    """Execute raw sql query"""
    engine = ctx.obj['engine']
    database_url = ctx.obj['database_url']
    metadata = ctx.obj['metadata']
    from sqlalchemy.sql import text
    # init tables first
    init_tables(database_url, metadata)
    stmt = text(sql)
    with engine.connect() as conn:
        results = conn.execute(stmt).fetchall()
    click.echo(json.dumps(results))


@cli.command(name='load-accounts')
@click.argument('accounts_file')
@click.pass_context
def load_accounts(ctx, accounts_file):
    """Execute raw sql query"""
    from sbds.storages.db.tasks import task_load_account_names
    database_url = ctx.obj['database_url']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task_load_account_names(database_url=database_url,
                                                    accounts_file=accounts_file))
