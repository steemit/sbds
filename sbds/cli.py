# -*- coding: utf-8 -*-
import ujson as json
import concurrent.futures

import click

from steemapi.steemnoderpc import SteemNodeRPC

import sbds.logging
from sbds.utils import block_num_from_previous
from sbds.utils import chunkify
from sbds.http_client import SimpleSteemAPIClient
from sbds.ws_client import SimpleSteemWSAPI
from sbds.ws_client import GrapheneWebsocketRPC

logger = sbds.logging.getLogger(__name__)

def parse_block_nums(ctx, param, value):
    if not value:
        return None
    try:
        block_nums =json.load(value)
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
                metavar="INTEGER BLOCK_NUM",
                type=click.IntRange(min=1))
@click.option('--end',
                help='Ending block_num, default is infinity',
              metavar="INTEGER BLOCK_NUM",
                type=click.IntRange(min=0),
                default=None)
def cli(server, block_nums, start, end):
    '''Output blocks from steemd in JSON format.

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
    '''
    # Setup steemd source
    rpc = SteemNodeRPC(server)

    for block in stream_blocks(rpc, start):
        click.echo(json.dumps(block, ensure_ascii=False).encode('utf8'))


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
        yield block

@click.command()
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=9000000)
@click.option('--chunksize', type=click.INT, default=100)
@click.option('--max_workers', type=click.INT, default=10)
@click.option('--url',
                metavar='STEEMD_HTTP_URL',
                envvar='STEEMD_HTTP_URL',
                help='Steemd HTTP server URL')
def bulk_blocks(start, end, chunksize, max_workers, url):
    for block in get_blocks_fast(start, end, chunksize, max_workers, None, url):
        click.echo(json.dumps(block, ensure_ascii=False).encode('utf8'))


def get_blocks_fast(start=1, end=9000000, chunksize=100, max_workers=5, rpc=None, url=None):
    extra = dict(start=start, end=end, chunksize=chunksize, max_workers=max_workers, rpc=rpc, url=url)
    logger.debug('get_blocks_fast',extra=extra)
    rpc = rpc or SimpleSteemAPIClient(url)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, chunk in enumerate(chunkify(range(start, end), chunksize=chunksize), 1):
            logger.debug('get_block_fast loop', extra=dict(chunk_count=i))
            for b in executor.map(rpc.get_block, chunk):
                 block_num = block_num_from_previous(b['previous'])
                 b.update(block_num=block_num)
                 yield b
