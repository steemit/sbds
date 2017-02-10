# -*- coding: utf-8 -*-
import concurrent.futures
import fileinput
import fnmatch
import json
import os

import click
import toolz.itertoolz
from steemapi.steemnoderpc import SteemNodeRPC

import sbds.checkpoint
from sbds.checkpoint import checkpoint_opener_wrapper
import sbds.logging
from sbds.http_client import SimpleSteemAPIClient
from sbds.utils import chunkify

logger = sbds.logging.getLogger(__name__)


# noinspection PyUnusedLocal
def parse_block_nums(ctx, param, value):
    if not value:
        return None
    try:
        block_nums = json.load(value)
    except:
        raise click.BadParameter('Must be valid JSON array')
    if not isinstance(block_nums, list):
        raise click.BadParameter('Must be valid JSON array')
    else:
        return block_nums


@click.command()
@click.option('--server',
              metavar='WEBSOCKET_URL',
              envvar='WEBSOCKET_URL',
              help='Steemd server URL',
              default='wss://steemd.steemitdev.com:443')
@click.option('--block_nums',
              type=click.File('r'),
              required=False,
              callback=parse_block_nums)
@click.option('--start',
              help='Starting block_num, default is 1',
              default=1,
              envvar='STARTING_BLOCK_NUM',
              type=click.IntRange(min=1))
@click.option('--end',
              help='Ending block_num, default is infinity',
              metavar="INTEGER BLOCK_NUM",
              type=click.IntRange(min=0),
              default=None)
def cli(server, block_nums, start, end):
    """Output blocks from steemd in JSON format.

    \b
    Which Steemd:
    \b
    1. CLI "--server" option if provided
    2. ENV var "WEBSOCKET_URL" if provided
    3. Default: "wss://steemit.com/wspa"

    \b
    Which Blocks To Output:
    \b
    - Stream blocks beginning with current block by omitting --start, --end, and BLOCKS
    - Fetch a range of blocks using --start and/or --end
    - Fetch list of blocks by passing BLOCKS a JSON array of block numbers (either filename or "-" for STDIN)

    Where To Output Blocks:

    \b
    2. ENV var "BLOCKS_OUT" if provided
    3. Default: STDOUT
    """
    # Setup steemd source
    rpc = SteemNodeRPC(server)
    with click.open_file('-', 'w', encoding='utf8') as f:
        if block_nums:
            blocks = get_blocks(rpc, block_nums)
        elif start and end:
            blocks = get_blocks(rpc, range(start, end))
        else:
            blocks = rpc.block_stream(start)

        json_blocks = map(json.dumps, blocks)

        for block in json_blocks:
            click.echo(block, file=f)


@click.command()
@click.option('--url',
              metavar='STEEMD_HTTP_URL',
              envvar='STEEMD_HTTP_URL',
              help='Steemd HTTP server URL')
def block_height(url):
    rpc = SimpleSteemAPIClient(url)
    click.echo(rpc.last_irreversible_block_num())


def stream_blocks(rpc, start):
    for block in rpc.block_stream(start=start):
        yield block


def get_blocks(rpc, block_nums):
    for block in map(rpc.get_block, block_nums):
        yield block


@click.command(name='bulk-blocks')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=0)
@click.option('--chunksize', type=click.INT, default=100)
@click.option('--max_workers', type=click.INT, default=None)
@click.option('--url',
              metavar='STEEMD_HTTP_URL',
              envvar='STEEMD_HTTP_URL',
              help='Steemd HTTP server URL')
def bulk_blocks(start, end, chunksize, max_workers, url):
    """Quickly request blocks from steemd"""

    rpc = SimpleSteemAPIClient(url)
    if end == 0:
        end = rpc.last_irreversible_block_num()

    with click.open_file('-', 'w', encoding='utf8') as f:
        blocks = get_blocks_fast(start, end, chunksize, max_workers, None, url)
        json_blocks = map(json.dumps, blocks)
        for block in json_blocks:
            click.echo(block.encode('utf8'), file=f)


def get_blocks_fast(start=None, end=None, chunksize=None, max_workers=None,
                    rpc=None, url=None):
    extra = dict(start=start, end=end, chunksize=chunksize,
                 max_workers=max_workers, rpc=rpc, url=url)
    logger.debug('get_blocks_fast', extra=extra)
    rpc = rpc or SimpleSteemAPIClient(url)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, chunk in enumerate(chunkify(range(start, end), chunksize=chunksize), 1):
            logger.debug('get_block_fast loop', extra=dict(chunk_count=i))
            for b in executor.map(rpc.get_block, chunk):
                yield b



@click.command(name='load-checkpoint-blocks')
@click.argument('checkpoints_path',
                type=click.STRING,
                envvar='CHECKPOINTS_PATH')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=0)
def load_blocks_from_checkpoints(checkpoints_path, start, end):
    """Load blocks from checkpoints"""

    checkpoint_set = sbds.checkpoint.required_checkpoints_for_range(path=checkpoints_path,
                                                                    start=start, end=end)
    total_blocks_to_load = end - start

    with fileinput.FileInput(mode='r',
                             files=checkpoint_set.checkpoint_paths,
                             openhook=checkpoint_opener_wrapper(encoding='utf8')) as blocks:

        blocks = toolz.itertoolz.drop(checkpoint_set.initial_checkpoint_offset,
                                      blocks)
        if total_blocks_to_load > 0:
            with click.open_file('-', 'w', encoding='utf8') as f:
                for i, block in enumerate(blocks, 1):
                    click.echo(block.strip().encode('utf8'))
                    if i == total_blocks_to_load:
                        break
        else:
            with click.open_file('-', 'w', encoding='utf8') as f:
                for block in blocks:
                    click.echo(block.strip().encode('utf8'), file=f)



@click.command(name='test-checkpoint-access')
@click.argument('checkpoints_path',
                type=click.STRING,
                envvar='CHECKPOINTS_PATH')
@click.pass_context
def test_checkpoint_access(ctx, checkpoints_path):
    """Test checkpoint access"""
    try:
        checkpoint_set = sbds.checkpoint.required_checkpoints_for_range(
            path=checkpoints_path,
            start=1, end=0)
        with fileinput.FileInput(mode='r',
                                 files=checkpoint_set.checkpoint_paths,
                                 openhook=checkpoint_opener_wrapper(encoding='utf8')) as blocks:

           for i, block in enumerate(blocks):
                block_num = json.loads(block)['block_num']
                if block_num:
                    click.echo('Success: loaded block %s' % block_num, err=True)
                    ctx.exit(code=0)
                else:
                    click.echo('Failed to load block', err=True)
                    ctx.exit(code=127)
    except Exception as e:
        click.echo('Fail: %s' % e, err=True)
        ctx.exit(code=127)