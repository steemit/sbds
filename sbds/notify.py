# -*- coding: utf-8 -*-

import click

from pprint import pformat
import sys
import json

from .utils import block_num_from_previous


@click.command()
@click.argument('blocks', default=click.get_text_stream('stdin'))
def notify(blocks):
    for block in blocks:
        try:
            block = json.loads(block)
            previous_block_hash = block['params'][1][0]['previous']
            blocknum = block_num_from_previous(previous_block_hash)
            block['blocknum'] = blocknum
            click.echo(block)
        except Exception as e:
            print(e, file=sys.stderr, flush=True)
