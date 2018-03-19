# -*- coding: utf-8 -*-

import json
import click
import shutil
import os
import pathlib
import requests
import structlog

from sbds.sbds_json import dumps

logger = structlog.get_logger(__name__)


def fetch(session, steemd_url, block_num, method):
    if method == 'get_block':
        jsonrpc_data = dict(id=block_num, jsonrpc='2.0', method=method,
                            params=[block_num])
    elif method == 'get_ops_in_block':
        jsonrpc_data = dict(id=block_num, jsonrpc='2.0', method=method,
                            params=[block_num, False])
    else:
        raise ValueError('unknown method %s' % method)
    response = session.post(steemd_url, json=jsonrpc_data)
    response.raise_for_status()
    response_json = response.json()
    response_raw = response.content
    assert 'error' not in response_json
    assert response_json['id'] == block_num
    return response_raw, response_json

def key(block_num, name, base_path, subdir_prefix_len):
    block_num_str = str(block_num)
    if len(block_num_str) <= subdir_prefix_len:
        return pathlib.PosixPath(os.path.join(base_path,block_num_str, f'{name}'))
    else:
        subdir = str(block_num)[:subdir_prefix_len]
        dir = str(block_num)[subdir_prefix_len:]
        return pathlib.PosixPath(os.path.join(base_path,subdir,dir,f'{name}'))

def put(pathobj, data):
    pathobj.write_bytes(dumps(data).encode())


@click.group(name='fs')
@click.option('--path', type=click.Path(file_okay=False), default='blocks_data')
@click.option('--subdir_prefix_length', type=click.INT, default=4)
@click.pass_context
def fs(ctx, path, subdir_prefix_length):
    """Interact with a filesystem storage backend"""
    ctx.obj = dict(path=path,
                   subdir_prefix_length=subdir_prefix_length
                   )


@fs.command('init')
@click.pass_context
def init(ctx):
    """Create path to store blocks"""
    range_max = int(ctx.obj['subdir_prefix_length'] * '9')
    base_path = ctx.obj['path']
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    for subdir in range(1, range_max):
        path = os.path.join(base_path,str(subdir))
        if not os.path.exists(path):
            os.mkdir(path)


@fs.command(name='put-blocks-and-ops')
@click.argument('steemd_url', type=click.STRING, default='https://api.steemit.com')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT,default=20000000)
@click.pass_context
def put_blocks_and_ops(ctx, steemd_url, start, end):
    session = requests.Session()
    subdir_prefix_len = ctx.obj['subdir_prefix_length']
    base_path = ctx.obj['path']
    for block_num in range(start, end+1):
        try:
            raw, block = fetch(session, steemd_url, block_num, 'get_block')

            block_key = key(block_num, 'block.json', base_path, subdir_prefix_len)
            block = block['result']
            put(block_key, block)
            logger.info('put block',block_num=block_num, key=block_key)

            raw, ops = fetch(session, steemd_url, block_num, 'get_ops_in_block')
            ops_key = key(block_num, 'ops_in_block.json', base_path, subdir_prefix_len)
            ops = ops['result']
            put(ops_key, ops)
            logger.info('put ops_in_block', block_num=block_num, key=ops_key)
        except Exception as e:
            click.echo(str(e),err=True)
