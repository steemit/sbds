# -*- coding: utf-8 -*-
import ujson as json
from itertools import chain
from functools import partial

import click
import certifi
import elasticsearch
import elasticsearch_dsl
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Index
from elasticsearch.helpers import streaming_bulk

import sbds.logging
from sbds.storages.elasticsearch import Block
from sbds.storages.elasticsearch import prepare_bulk_block
from sbds.http_client import SimpleSteemAPIClient

logger = sbds.logging.getLogger(__name__)


@click.group()
@click.option('--elasticsearch_url', type=click.STRING, envvar='ELASTICSEARCH_URL',
              help='Elastic connection URL, read from "ELASTICSEARCH_URL" ENV var by default')
@click.option('--index', type=click.STRING, default='blocks')
@click.pass_context
def es(ctx, elasticsearch_url, index):
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
    connections.create_connection(hosts=[elasticsearch_url])
    ctx.obj = dict(es=es, index=index)
    ctx.obj['elasticsearch_url'] = elasticsearch_url

@es.command()
@click.pass_context
def test(ctx):
    """Test connection to database"""
    es = ctx.obj['es']
    click.echo(es.info())


@es.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    """Insert or update blocks in the database, accepts "-" for STDIN (default)"""
    es = ctx.obj['es']

    es_blocks = map(Block.from_block, blocks)
    for es_block in es_blocks:
        es_block.save()


@es.command(name='init')
@click.confirmation_option(prompt='Are you sure you want to create the db?')
@click.pass_context
def init_db(ctx):
    """Create any missing tables on the database"""
    es = ctx.obj['es']
    index = ctx.obj['index']
    block_storage = Block(using=es)
    block_storage.init()


@es.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the db?')
@click.pass_context
def reset_db(ctx):
    """Drop and then create tables on the database"""
    es = ctx.obj['es']
    index = Index(using=ctx.obj['index'])
    index.delete()
    index.create()


@es.command(name='insert-bulk-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_bulk_blocks(ctx, blocks):
    """Insert or update blocks in the database, accepts "-" for STDIN (default)"""
    es = elasticsearch.Elasticsearch(hosts=[ctx.obj['elasticsearch_url']])

    actions = map(prepare_bulk_block, blocks)
    results = streaming_bulk(es, actions=actions)
    for r in results:
        click.echo(r)