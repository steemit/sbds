# -*- coding: utf-8 -*-

import json
import click
import shutil
import os
import pathlib
import requests
import structlog
import hashlib

from sbds.sbds_json import dumps
from . import FileSystemStorage

logger = structlog.get_logger(__name__)

CHARS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']


def fetch_from_chain(session, source_url, block_num, method):
    if method == 'get_block':
        jsonrpc_data = dict(id=block_num, jsonrpc='2.0', method=method,
                            params=[block_num])
    elif method == 'get_ops_in_block':
        jsonrpc_data = dict(id=block_num, jsonrpc='2.0', method=method,
                            params=[block_num, False])
    else:
        raise ValueError('unknown method %s' % method)
    response = session.post(source_url, json=jsonrpc_data)
    response.raise_for_status()
    response_json = response.json()
    response_raw = response.content
    assert 'error' not in response_json
    assert response_json['id'] == block_num
    return response_raw, response_json


def key(block_num, name, base_path):
    block_num_sha = hashlib.sha1(bytes(block_num)).hexdigest()
    return pathlib.PosixPath(os.path.join(
        base_path, block_num_sha[:2], block_num_sha[2:4], block_num_sha[4:6], str(block_num), f'{name}'))


def put(pathobj, data):
    pathobj.parent.mkdir(parents=True, exist_ok=True)
    pathobj.write_bytes(dumps(data).encode())


@click.group(name='fs')
@click.option('--uri',
              type=click.STRING,
              help='the uri for the storage path: "file:///<path>/"')
@click.pass_context
def fs(ctx, uri):
    """Interact with a filesystem storage backend"""
    fs = FileSystemStorage(uri=uri)
    ctx.obj = dict(storage=fs)


@fs.command('init')
@click.pass_context
def init(ctx):
    """Create path to store blocks"""
    storage = ctx.obj['storage']
    click.echo(f'initializing storage at {storage.uri}')
    storage.init()


@fs.command(name='put-blocks-and-ops')
@click.argument('--source_uri', type=click.STRING)
@click.option('--start_block', type=click.INT, default=1)
@click.option('--end_block', type=click.INT, default=20000000)
@click.option('--skip_existing', type=click.BOOL, default=True)
@click.pass_context
def put_blocks_and_ops(ctx, source_uri, start_block, end_block, skip_existing):
    session = requests.Session()
    base_path = ctx.obj['path']
    for block_num in range(start_block, end_block + 1):
        ops_key = None
        block_key = None
        try:
            block_key = key(block_num, 'block.json', base_path)
            if skip_existing and block_key.exists():
                logger.info('put blocks', block_num=block_num, key=block_key, exists=True)
                continue

            raw, block = fetch_from_chain(session, source_url, block_num, 'get_block')
            block = block['result']
            put(block_key, block)
            logger.info('put_blocks_and_ops', block_num=block_num, key=block_key)

            ops_key = key(block_num, 'ops_in_block.json', base_path)
            if skip_existing and ops_key.exists():
                logger.info('put ops', block_num=block_num, key=ops_key,
                            exists=True)
                continue
            raw, ops = fetch_from_chain(session, source_url, block_num, 'get_ops_in_block')
            ops = ops['result']
            put(ops_key, ops)
            logger.info('put_blocks_and_ops', block_num=block_num, key=ops_key)
        except Exception as e:
            logger.error('put_blocks_and_ops', error=e, block_num=block_num,
                         block_key=block_key, ops_key=ops_key)


@fs.command(name='put-blocks')
@click.argument('source_url', type=click.STRING, default='https://api.steemit.com')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=20000000)
@click.option('--skip_existing', type=click.BOOL, default=True)
@click.pass_context
def put_blocks(ctx, source_url, start, end, skip_existing):
    session = requests.Session()
    base_path = ctx.obj['path']
    for block_num in range(start, end + 1):
        block_key = None
        try:
            block_key = key(block_num, 'block.json', base_path)
            if skip_existing and block_key.exists():
                logger.info('put blocks', block_num=block_num, key=block_key, exists=True)
                continue
            raw, block = fetch_from_chain(session, source_url, block_num, 'get_block')
            block = block['result']
            put(block_key, block)
            logger.info('put_blocks', block_num=block_num, key=block_key)

        except Exception as e:
            logger.error('put_blocks', error=e, block_num=block_num, key=block_key)


@fs.command(name='put-ops')
@click.argument('source_url', type=click.STRING, default='https://api.steemit.com')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=20000000)
@click.option('--skip_existing', type=click.BOOL, default=True)
@click.pass_context
def put_ops(ctx, source_url, start, end, skip_existing):
    session = requests.Session()
    base_path = ctx.obj['path']
    for block_num in range(start, end + 1):
        ops_key = None
        try:
            ops_key = key(block_num, 'ops.json', base_path)
            if skip_existing and ops_key.exists():
                logger.info('put_ops', block_num=block_num, key=ops_key,
                            exists=True)
                continue
            raw, ops = fetch_from_chain(session, source_url, block_num, 'get_ops_in_block')
            ops = ops['result']
            put(ops_key, ops)
            logger.info('put ops', block_num=block_num, key=ops_key)
        except Exception as e:
            logger.error('put_ops', error=e, block_num=block_num, key=ops_key)
