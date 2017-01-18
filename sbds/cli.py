# -*- coding: utf-8 -*-
import json
import concurrent.futures
import fnmatch
import os
import fileinput
import operator
from itertools import chain

import click

from steemapi.steemnoderpc import SteemNodeRPC

import sbds.logging
from sbds.utils import block_num_from_previous
from sbds.utils import chunkify
from sbds.http_client import SimpleSteemAPIClient
from sbds.ws_client import SimpleSteemWSAPI
from sbds.ws_client import GrapheneWebsocketRPC

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
            click.echo(block.encode('utf8'), file=f)

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
        block_num = block_num_from_previous(block['previous'])
        block.update(block_num=block_num)
        yield block


def get_blocks(rpc, block_nums):
    for block in map(rpc.get_block, block_nums):
        block_num = block_num_from_previous(block['previous'])
        block.update(block_num=block_num)
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
    '''Quickly request blocks from steemd'''
    with click.open_file('-', 'w', encoding='utf8') as f:
        blocks = get_blocks_fast(start, end, chunksize, max_workers, None, url)
        json_blocks = map(json.dumps, blocks)
        for block in json_blocks:
            click.echo(block.encode('utf8'), file=f)


def get_blocks_fast(start=None, end=None, chunksize=None, max_workers=None, rpc=None, url=None):
    extra = dict(start=start, end=end, chunksize=chunksize, max_workers=max_workers, rpc=rpc, url=url)
    logger.debug('get_blocks_fast', extra=extra)
    rpc = rpc or SimpleSteemAPIClient(url)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, chunk in enumerate(chunkify(range(start, end), chunksize=chunksize), 1):
            logger.debug('get_block_fast loop', extra=dict(chunk_count=i))
            for b in executor.map(rpc.get_block, chunk):
                block_num = block_num_from_previous(b['previous'])
                b.update(block_num=block_num)
                yield b


@click.command(name='load-checkpoint-blocks')
@click.argument('checkpoints_dir', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=0)
def load_blocks_from_checkpoints(checkpoints_dir, start, end):
    '''Load blocks from locally stored "checkpoint" files'''
    checkpoint_filenames = required_checkpoint_files(path=checkpoints_dir, start=start, end=end)
    checkpoint_filenames = sorted(checkpoint_filenames)
    display_load_blocks_info(checkpoints_dir, start, end, checkpoint_filenames)
    with fileinput.FileInput(mode='r',
                    files=checkpoint_filenames,
                   openhook=hook_compressed_encoded('utf8')) as blocks:
        for block in blocks:
            block = json.loads(block)
            block_num = block_num_from_previous(block['previous'])
            if block_num < start:
                continue
            if end and end > 0 and block_num > end:
                break
            block['block_num'] = block_num
            click.echo(json.dumps(block,ensure_ascii=True).encode('utf8'))

def display_load_blocks_info(checkpoints_dir, start, end, checkpoint_filenames):
    import os
    checkpoints=os.linesep.join([click.format_filename(fn) for fn in checkpoint_filenames])
    output='''
Loading blocks from checkpoints
===============================
start:         {start}
end:           {end}
total blocks:  {total_blocks}
checkpoints:
{checkpoints}

'''.format(start=start, end=end, total_blocks=end-start,
               checkpoints=checkpoints)
    click.echo(output, err=True)


def required_checkpoint_files(path, start, end=None, files=None):
    checkpoint_file_pattern = 'blocks_*.json*'
    all_files = os.listdir(path)
    files = files or fnmatch.filter(all_files, checkpoint_file_pattern)
    checkpoint_files = []
    for file in files:
        check_low = int(file.split('-')[0].split('_')[1])
        check_high = int(file.split('-')[1].split('.')[0])
        if start > check_high:
            continue
        if end and end > 0 and check_low > end:
            break
        checkpoint_files.append(file)

    return [os.path.join(path, f) for f in checkpoint_files]


def roundup(x, factor=1000000):
    return x if x % factor == 0 else x + factor - x % factor


def rounddown(x, factor=1000000):
    return ((x // factor) * factor)


def hook_compressed_encoded(encoding, real_mode='rt'):
    def openhook_compressed(filename, mode):
        ext = os.path.splitext(filename)[1]
        if ext == '.gz':
            import gzip
            return gzip.open(filename, mode=real_mode, encoding=encoding)
        elif ext == '.bz2':
            import bz2
            return bz2.BZ2File(filename, mode=real_mode,encoding=encoding)
        else:
            return open(filename, mode=real_mode, encoding=encoding)
    return openhook_compressed
