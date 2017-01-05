# -*- coding: utf-8 -*-
import json

import click

from steemapi.steemnoderpc import SteemNodeRPC

import sbds.logging
logger = sbds.logging.getLogger(__name__)

def parse_blocknums(ctx, param, value):
    if not value:
        return None
    try:
        return json.load(value)
    except:
        return None

@click.command()
@click.option('--server',
                metavar='WEBSOCKET_URL',
                envvar='WEBSOCKET_URL',
                help='Specify API server',
              default='wss://steemit.com/wspa')
@click.argument('blocks',
              type=click.File('r'),
              required=False,
              callback=parse_blocknums)
@click.option('--start',
                help='Starting block number, default is 0',
                default=0,
                type=int)
@click.option('--end',
                help='Ending block number, default is continuous',
                type=int)
@click.option('--pretty/--no-pretty',
                help='Pretty print, default is no pretty print',
                default=None)
def cli(server, blocks, start, end, pretty):
    '''Stream Steem blocks to stdout. You may specify blocks to fetch in several ways:

    Stream blocks with beginning with current block by omitting --start, --end, and BLOCKS

    Fetch a range of blocks using --start and/or --end

    Fetch list of blocks by passing BLOCKS a JSON array of block numbers (either filename or "-" for STDIN)

    '''
    rpc = SteemNodeRPC(server)
    if blocks:
        for block in get_blocks(rpc, blocks):
            click.echo(json.dumps(block, indent=pretty))
    else:
        for block in stream_blocks(rpc, start, end):
            click.echo(json.dumps(block, indent=pretty))


def get_blocks(rpc, blocknums):
    # Blocks from start until head block
    for blocknum in blocknums:
        # Get full block
        block = rpc.get_block(blocknum)
        block.update({"block_num": blocknum})
        yield block

def stream_blocks(rpc, start, end):
    for block in rpc.block_stream(start=start):
        yield block
