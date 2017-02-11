# -*- coding: utf-8 -*-
from itertools import chain

import certifi
import click
import elasticsearch
from elasticsearch.helpers import streaming_bulk
from elasticsearch_dsl.connections import connections

import sbds.logging
from sbds.storages.elasticsearch import Operation
from sbds.storages.elasticsearch import extract_bulk_operation_from_block
from sbds.storages.elasticsearch import extract_operations_from_block

logger = sbds.logging.getLogger(__name__)


@click.group()
@click.option('--elasticsearch_url', type=click.STRING, envvar='ELASTICSEARCH_URL',
              help='Elastic connection URL, read from "ELASTICSEARCH_URL" ENV var by default')
@click.option('--index', type=click.STRING, default='blocks')
@click.pass_context
def es(ctx, elasticsearch_url, index):
    """Group of commands used to interact with the elasticsearch storage backend.
        Typical usage would be reading blocks in JSON format from STDIN
        and then storing those blocks in the index:

        \b
        sbds | es insert-blocks

        In the example above, the "sbds" command streams new blocks to STDOUT, which are piped to STDIN of
        the "insert-blocks" db command by default. The "database_url" was read from the "DATABASE_URL"
        ENV var, though it may optionally be provided on the command line:

        \b
        db --elasticsearch_url 'http[s]://user:password@host/index[?key=value..]' tests

    """
    esd = connections.create_connection(hosts=[elasticsearch_url],
                                        port=443,
                                        use_ssl=True,
                                        verify_certs=True,
                                        ca_certs=certifi.where(), )
    ctx.obj = dict(esd=esd, index=index, elasticsearch_url=elasticsearch_url)


@es.command()
@click.pass_context
def test(ctx):
    """Test connection to elasticsearch"""
    esd = ctx.obj['esd']
    click.echo(esd.info())


# noinspection PyUnusedLocal
@es.command(name='insert-blocks')
@click.argument('blocks', type=click.File('r', encoding='utf8'), default='-')
@click.pass_context
def insert_blocks(ctx, blocks):
    """Insert or update blocks in the index, accepts "-" for STDIN (default)"""

    for i, block in enumerate(blocks):
        for operation_dict in extract_operations_from_block(block):
            try:
                o = Operation(**operation_dict)
                o.save()
            except Exception as e:
                logger.exception(e)


@es.command(name='init')
@click.confirmation_option(prompt='Are you sure you want to create the index?')
@click.pass_context
def init_es(ctx):
    """Create any missing mappings on the index"""
    es = elasticsearch.Elasticsearch([ctx.obj['elasticsearch_url']])
    index = ctx.obj['index']
    try:
        es.indices.create(index)
    except Exception as e:
        click.echo(e)
    block_storage = Operation(using=es)
    block_storage.init()


@es.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to drop and then create the index?')
@click.pass_context
def reset_es(ctx):
    """Drop and then create the index and mappings"""
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
@click.option('--raise-on-error/--no-raise-on-error', is_flag=True, default=True)
@click.option('--raise-on-exception/--no-raise-on-exception', is_flag=True, default=True)
@click.pass_context
def insert_bulk_blocks(ctx, blocks, raise_on_error, raise_on_exception):
    """Insert or update blocks in the index, accepts "-" for STDIN (default)"""
    es = elasticsearch.Elasticsearch(hosts=[ctx.obj['elasticsearch_url']],
                                     port=443,
                                     use_ssl=True,
                                     verify_certs=True,
                                     ca_certs=certifi.where(),
                                     maxsize=10,
                                     block=True,
                                     timeout=10
                                     )

    actions = chain.from_iterable(map(extract_bulk_operation_from_block, blocks))
    results = streaming_bulk(es, chunk_size=2000, max_chunk_bytes=10485760, actions=actions,
                             raise_on_error=raise_on_error,
                             raise_on_exception=raise_on_exception)

    for status, details in results:
        if status is False:
            click.echo(details, err=True)
