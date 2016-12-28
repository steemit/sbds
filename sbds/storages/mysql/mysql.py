# -*- coding: utf-8 -*-

import sbds.logging
logger = sbds.logging.getLogger(__name__)

import mysql.connector
from mysql.connector import errorcode
import click

from .url import URL


ADD_BLOCK_SQL = 'INSERT INTO Blocks (raw) VALUES (%(raw)s)'


# support DATABASE_URL ENV variable parsing
# db_url = URL.from_env()


@click.group(name='db')
@click.option('database_url', type=str, envvar='DATABASE_URL')
@click.pass_context
def db(ctx, database_url):
    db_url = URL.make_url(database_url)
    db_config = db_url.translate_connect_args()
    db_config.update(
        {
            'raise_on_warnings': True,
            'use_pure': True,
            'autocommit': True,
            'user': db_config['username']}
    )
    del db_config['username']
    cnx = mysql.connector.connect(**db_config)
    ctx.obj = dict(CNX=cnx, DB_CONFIG=db_config)


@db.command()
@click.pass_context
def can_connect(ctx):
    click.echo(ctx.obj['CNX'].is_connected())

@db.command()
@click.argument('sql', type=str)
@click.pass_context
def query(ctx,sql):
    cursor = ctx.obj['CNX'].cursor()
    for row in cursor.execute(sql):
        click.echo(row)


@db.command()
@click.argument('blocks', type=click.File('r'))
@click.pass_context
def insert_blocks(ctx, blocks):
    cursor = ctx.obj['CNX'].cursor()
    count = 0
    failed = 0
    for block in blocks:
        try:
            add_block(cursor, block)
            count += 1
            click.echo('Added {} blocks'.format(count))
        except:
            failed += 1
            click.echo('Failed {} blocks'.format(failed))

@db.command()
@click.pass_context
def create_database(ctx):
    cursor = ctx.obj['CNX'].cursor()
    database = ctx.obj['DB_CONFIG']['database']
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {}".format(database))
    except mysql.connector.Error as err:
        click.Exception("Failed creating database: {}".format(err))


@db.command()
@click.pass_context
def drop_database(ctx):
    cursor = ctx.obj['CNX'].cursor()
    database = ctx.obj['DB_CONFIG']['database']
    try:
        cursor.execute(
            "DROP DATABASE IF EXISTS {} ".format(database))
    except mysql.connector.Error as err:
        click.Exception("Failed creating database: {}".format(err))


@db.command()
@click.pass_context
def create_tables(ctx):
    cnx = ctx.obj['CNX']
    cursor = ctx.obj['CNX'].cursor()
    database = ctx.obj['DB_CONFIG']['database']
    tables = get_tables()
    try:
        cnx.database = database
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor, database)
            cnx.database = database
        else:
            pass
    cursor.execute(tables)


def get_tables(tables_file='tables.sql'):
    with open('tables.sql', 'r') as f:
        tables = f.read()
    return tables


def add_block(cursor, block, add_block_sql=ADD_BLOCK_SQL):
    cursor.execute(add_block_sql, dict(raw=block))
