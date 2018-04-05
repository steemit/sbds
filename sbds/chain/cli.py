# -*- coding: utf-8 -*-
import concurrent.futures
import json

import click

import structlog
from sbds.http_client import SimpleSteemAPIClient
from sbds.utils import chunkify

logger = structlog.get_logger(__name__)


@click.group(name='chain')
def cli():
    """Query the Steem blockchain"""


@cli.command(name='stream-blocks')
@click.option(
    '--url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    default='https://steemd.steemitdev.com',
    help='Steemd HTTP server URL')
@click.option('--block_nums', type=click.File('r'))
@click.option(
    '--start',
    help='Starting block_num, default is 1',
    default=1,
    envvar='STARTING_BLOCK_NUM',
    type=click.IntRange(min=1))
@click.option(
    '--end',
    help='Ending block_num, default is infinity',
    metavar="INTEGER BLOCK_NUM",
    type=click.IntRange(min=0),
    default=None)
def stream_blocks(url, block_nums, start, end):
    """Stream blocks from steemd in JSON format

    \b
    Which Steemd:
    \b
    1. CLI "--url" option if provided
    2. ENV var "STEEMD_HTTP_URL" if provided
    3. Default: "https://steemd.steemitdev.com"

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
    rpc = SimpleSteemAPIClient(url)
    with click.open_file('-', 'w', encoding='utf8') as f:
        if block_nums:
            block_nums = json.load(block_nums)
            blocks = _stream_blocks(rpc, block_nums)
        elif start and end:
            blocks = _stream_blocks(rpc, range(start, end))
        else:
            blocks = rpc.stream(start)

        json_blocks = map(json.dumps, blocks)

        for block in json_blocks:
            click.echo(block, file=f)


def _stream_blocks(rpc, block_nums):
    for block in map(rpc.get_block, block_nums):
        yield block


@cli.command()
@click.option(
    '--url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    help='Steemd HTTP server URL')
def block_height(url):
    rpc = SimpleSteemAPIClient(url)
    click.echo(rpc.last_irreversible_block_num())


@cli.command(name='get-blocks')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=0)
@click.option('--chunksize', type=click.INT, default=100)
@click.option('--max_workers', type=click.INT, default=None)
@click.option(
    '--url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    help='Steemd HTTP server URL')
def get_blocks_fast(start, end, chunksize, max_workers, url):
    """Request blocks from steemd in JSON format"""

    rpc = SimpleSteemAPIClient(url)
    if end == 0:
        end = rpc.last_irreversible_block_num()

    with click.open_file('-', 'w', encoding='utf8') as f:
        blocks = _get_blocks_fast(
            start=start,
            end=end,
            chunksize=chunksize,
            max_workers=max_workers,
            rpc=rpc,
            url=url)
        json_blocks = map(json.dumps, blocks)
        for block in json_blocks:
            click.echo(block.encode('utf8'), file=f)


# pylint: disable=too-many-arguments
def _get_blocks_fast(start=None,
                     end=None,
                     chunksize=None,
                     max_workers=None,
                     rpc=None,
                     url=None):
    extra = dict(
        start=start,
        end=end,
        chunksize=chunksize,
        max_workers=max_workers,
        rpc=rpc,
        url=url)
    logger.debug('get_blocks_fast', extra=extra)
    rpc = rpc or SimpleSteemAPIClient(url)
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers) as executor:
        for i, chunk in enumerate(
                chunkify(range(start, end), chunksize=chunksize), 1):
            logger.debug('get_block_fast loop', extra=dict(chunk_count=i))
            for b in executor.map(rpc.get_block, chunk):
                # dont yield anything when we encounter a null output
                # from an HTTP 503 error
                if b:
                    yield b
