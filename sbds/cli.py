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
    #rpc = SteemNodeRPC(server)
    rpc = SimpleSteemAPIClient()
    #rpc = SimpleSteemWSAPI(server)
    block_height = rpc.last_irreversible_block_num()
    for block in get_blocks_fast(rpc, range(1, block_height)):
        click.echo(json.dumps(block))


@click.command()
def block_height():
    rpc = SimpleSteemAPIClient()
    click.echo(rpc.last_irreversible_block_num())

def get_blocks(rpc, block_nums):
    # Blocks from start until head block
    blocks_requested = len(block_nums)
    for i, block_num in enumerate(block_nums,1):
        # Get full block
        blocks_remaining = blocks_requested - i
        block = rpc.get_block(block_num)
        block.update({"block_num": block_num})
        # logger.info(dict(blocks_retreived=i, blocks_requested=blocks_requested,
        #                blocks_remaining=blocks_remaining, block_num=block_num))
        yield block


def stream_blocks(rpc, start):
    for block in rpc.block_stream(start=start):
        block_num = block_num_from_previous(block['previous'])
        yield block

@click.command()
@click.option('--start', type=click.INT)
@click.option('--end', type=click.INT)
@click.option('--chunksize', type=click.INT)
@click.option('--max_workers', type=click.INT)
def bulk_blocks(start=1, end=9000000, chunksize=100000, max_workers=10):
    return get_blocks_fast(start, end, chunksize, max_workers, None)


def get_blocks_fast(start=1, end=9000000, chunksize=100000, max_workers=10, rpc=None):
    rpc = rpc or SimpleSteemAPIClient()
    for chunk in chunkify(range(start, end), chunksize=chunksize):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for b in executor.map(rpc.get_block, chunk):
                 block_num = block_num_from_previous(b['previous'])
                 b.update(block_num=block_num)
                 yield b
