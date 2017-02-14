# -*- coding: utf-8 -*-
import fileinput
import json

import click
import toolz

import sbds.checkpoints
import sbds.logging
from sbds.checkpoints import checkpoint_opener_wrapper

logger = sbds.logging.getLogger(__name__)


@click.group()
def checkpoints():
    """retrieve blocks from blockchain checkpoints"""
    pass


@checkpoints.command(name='get-blocks')
@click.argument(
    'checkpoints_path', type=click.STRING, envvar='CHECKPOINTS_PATH')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT, default=0)
def load_blocks_from_checkpoints(checkpoints_path, start, end):
    """Load blocks from checkpoints"""

    checkpoint_set = sbds.checkpoints.required_checkpoints_for_range(
        path=checkpoints_path, start=start, end=end)
    total_blocks_to_load = end - start

    with fileinput.FileInput(
            mode='r',
            files=checkpoint_set.checkpoint_paths,
            openhook=checkpoint_opener_wrapper(encoding='utf8')) as blocks:

        blocks = toolz.itertoolz.drop(checkpoint_set.initial_checkpoint_offset,
                                      blocks)
        if total_blocks_to_load > 0:
            with click.open_file('-', 'w', encoding='utf8') as f:
                for i, block in enumerate(blocks, 1):
                    click.echo(block.strip().encode('utf8'), file=f)
                    if i == total_blocks_to_load:
                        break
        else:
            with click.open_file('-', 'w', encoding='utf8') as f:
                for block in blocks:
                    click.echo(block.strip().encode('utf8'), file=f)


@checkpoints.command(name='test-access')
@click.argument(
    'checkpoints_path', type=click.STRING, envvar='CHECKPOINTS_PATH')
@click.pass_context
def test_checkpoint_access(ctx, checkpoints_path):
    """Test checkpoints access"""
    try:
        checkpoint_set = sbds.checkpoints.required_checkpoints_for_range(
            path=checkpoints_path, start=1, end=0)
        with fileinput.FileInput(
                mode='r',
                files=checkpoint_set.checkpoint_paths,
                openhook=checkpoint_opener_wrapper(encoding='utf8')) as blocks:

            for i, block in enumerate(blocks):
                block_num = json.loads(block)['block_num']
                if block_num:
                    click.echo(
                        'Success: loaded block %s' % block_num, err=True)
                    ctx.exit(code=0)
                else:
                    click.echo('Failed to load block', err=True)
                    ctx.exit(code=127)
    except Exception as e:
        click.echo('Fail: %s' % e, err=True)
        ctx.exit(code=127)
