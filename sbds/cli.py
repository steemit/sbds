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
              default='ws://steemd-dev5.us-east-1.elasticbeanstalk.com:80')
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


@click.command()
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=9000000)
@click.option('--chunksize', type=click.INT, default=1000)
@click.option('--max_workers', type=click.INT, default=None)
@click.option('--url',
              metavar='STEEMD_HTTP_URL',
              envvar='STEEMD_HTTP_URL',
              help='Steemd HTTP server URL')
def bulk_blocks(start, end, chunksize, max_workers, url):
    """Quickly request blocks from steemd"""
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
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers) as executor:
        for i, chunk in enumerate(
                chunkify(range(start, end), chunksize=chunksize), 1):
            logger.debug('get_block_fast loop', extra=dict(chunk_count=i))
            for b in executor.map(rpc.get_block, chunk):
                yield b


@click.command(name='load-checkpoint-blocks')
@click.argument('checkpoints_dir', type=click.Path(exists=True, file_okay=False,
                                                   resolve_path=True))
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=0)
def load_blocks_from_checkpoints(checkpoints_dir, start, end):
    """Load blocks from locally stored "checkpoint" files"""

    checkpoint_set = sbds.checkpoint.required_checkpoints(path=checkpoints_dir,
                                                          start=start, end=end)
    total_blocks_to_load = end - start

    with fileinput.FileInput(mode='r',
                             files=checkpoint_set.checkpoint_paths,
                             openhook=hook_compressed_encoded(
                                     'utf8')) as blocks:

        blocks = toolz.itertoolz.drop(checkpoint_set.initial_checkpoint_offset,
                                      blocks)

        if total_blocks_to_load > 0:
            for i, block in enumerate(blocks, 1):
                click.echo(json.dumps(json.loads(block)).encode('utf8'))
                if i == total_blocks_to_load:
                    break
        else:
            for block in blocks:
                click.echo(json.dumps(json.loads(block)).encode('utf8'))


@click.command(name='load-checkpoint-blocks')
@click.argument('checkpoints_dir', type=click.STRING)
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=0)
def load_blocks_from_checkpoints(checkpoints_dir, start, end):
    """Load blocks from locally stored "checkpoint" files"""

    checkpoint_set = sbds.checkpoint.required_checkpoints(path=checkpoints_dir,
                                                          start=start, end=end)
    total_blocks_to_load = end - start

    with fileinput.FileInput(mode='r',
                             files=checkpoint_set.checkpoint_paths,
                             openhook=hook_compressed_encoded(
                                     'utf8')) as blocks:

        blocks = toolz.itertoolz.drop(checkpoint_set.initial_checkpoint_offset,
                                      blocks)

        if total_blocks_to_load > 0:
            for i, block in enumerate(blocks, 1):
                click.echo(json.dumps(json.loads(block)).encode('utf8'))
                if i == total_blocks_to_load:
                    break
        else:
            for block in blocks:
                click.echo(json.dumps(json.loads(block)).encode('utf8'))


def hook_compressed_encoded(encoding, real_mode='rt'):
    def openhook_compressed(filename, mode):
        ext = os.path.splitext(filename)[1]
        logger.debug('checkpoint ext: %s', ext)
        # checkpoint stored in s3
        if filename.startswith('s3://'):
            logger.debug('loading s3 checkpoint: %s', filename)
            import boto3
            import io
            s3_resource = boto3.resource('s3')
            bucket, key = sbds.checkpoint.split_s3_bucket_key(filename)
            logger.debug('s3 object bucket:%s key:%s', bucket, key)
            object = s3_resource.Object(bucket, key)
            data = object.get()

            if ext == '.gz':
                logger.debug('opening s3 gzipped checkpoint: %s', filename)
                import gzip
                buffer = gzip.GzipFile(fileobj=data['Body'])

            else:
                logger.debug('opening s3 checkpoint: %s', filename)
                buffer = data['Body']
            return io.TextIOWrapper(buffer=buffer,
                                    encoding=encoding)
        else:
            # local checkpoint
            logger.debug('loading local checkpoint')
            if ext == '.gz':
                logger.debug('opening local gzipped checkpoint: %s', filename)
                import gzip
                return gzip.open(filename, mode=real_mode, encoding=encoding)

            else:
                logger.debug('opening local checkpoint: %s', filename)
                return open(filename, mode=real_mode, encoding=encoding)

    return openhook_compressed


