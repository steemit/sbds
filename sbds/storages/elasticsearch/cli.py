# -*- coding: utf-8 -*-
import ujson as json
from itertools import chain


import click
import certifi
import elasticsearch
import elasticsearch_dsl
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Index
from elasticsearch.helpers import streaming_bulk

import sbds.logging
from sbds.storages.elasticsearch import Operation
from sbds.storages.elasticsearch import all_from_block
from sbds.storages.elasticsearch import prepare_bulk_block
from sbds.storages.elasticsearch import prepare_block
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
    es = connections.create_connection(hosts=[elasticsearch_url],
                                       port=443,
                                        use_ssl=True,
                                        verify_certs=True,
                                        ca_certs=certifi.where(),)

    ctx.obj = dict(es=es, index=index,elasticsearch_url=elasticsearch_url)


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
    for i, block in enumerate(blocks):
        for operation_dict in prepare_block(block):
            try:
                o = Operation(**operation_dict)
                o.save()
            except Exception as e:
                logger.exception(e)


@es.command(name='init')
@click.confirmation_option(prompt='Are you sure you want to create the index?')
@click.pass_context
def init_es(ctx):
    """Create any missing tables on the database"""
    es = elasticsearch.Elasticsearch([ctx.obj['elasticsearch_url']])
    index = ctx.obj['index']

    try:
        es.indices.create(index)
        block_storage = Block(using=es)
        block_storage.init()
    except Exception as e:
        click.echo(e)

@es.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the index?')
@click.pass_context
def reset_es(ctx):
    """Drop and then create tables on the database"""
    es = elasticsearch.Elasticsearch([ctx.obj['elasticsearch_url']])
    index = ctx.obj['index']
    try:
        es.indices.delete(index)
    except Exception as e:
        click.echo(e)
    try:
        es.indices.create(index)
        block_storage = Operation(using=es)
        block_storage.init()
    except Exception as e:
        click.echo(e)



@es.command(name='insert-bulk-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_bulk_blocks(ctx, blocks):
    """Insert or update blocks in the database, accepts "-" for STDIN (default)"""

    es = elasticsearch.Elasticsearch(hosts=[ctx.obj['elasticsearch_url']],
                                     port=443,
                                     use_ssl=True,
                                     verify_certs=True,
                                     ca_certs=certifi.where(),
                                     maxsize=100,
                                     timeout=10
                                     )

    actions = chain.from_iterable(map(prepare_bulk_block, blocks))
    results = streaming_bulk(es, chunk_size=10,
                             actions=actions)

    for r in results:
        pass