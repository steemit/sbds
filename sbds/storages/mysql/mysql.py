# -*- coding: utf-8 -*-
import json
import sbds.logging
logger = sbds.logging.getLogger(__name__)


import click
from sqlalchemy import create_engine

from sbds.storages.mysql import Blocks
from sbds.storages.mysql import Transactions
from sbds.storages.mysql.tables import meta

# support DATABASE_URL ENV variable parsing
# db_url = URL.from_env()


@click.group()
@click.option('--database_url', type=str, envvar='DATABASE_URL')
@click.option('--echo/--no-echo', is_flag=True, default=True)
@click.pass_context
def db(ctx, database_url, echo):
    engine = create_engine(database_url, echo=echo, execution_options={'stream_results':True})
    ctx.obj = dict(engine=engine)

@db.command()
@click.pass_context
def test(ctx):
    engine = ctx.obj['engine']
    result = engine.execute('SHOW TABLES').fetchall()
    click.echo('Success! Connected to database and found %s tables' % (len(result)))


@db.command()
@click.argument('sql', type=str)
@click.pass_context
def query(ctx, sql):
    engine = ctx.obj['engine']
    click.echo(engine.execute(sql).fetchall())


@db.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    engine = ctx.obj['engine']
    block_storage = Blocks(engine=engine)
    for block in blocks:
        data = json.loads(block)
        block_storage[data['block_num']] = block


@db.command(name='init')
@click.pass_context
def init_db(ctx):
    engine = ctx.obj['engine']
    meta.create_all(engine=engine)

@db.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the db?')
@click.pass_context
def reset_db(ctx):
    engine = ctx.obj['engine']
    meta.drop_all(engine=engine)
    meta.create_all(engine=engine)