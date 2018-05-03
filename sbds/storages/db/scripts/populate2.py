# -*- coding: utf-8 -*-
import asyncio
import os

import click
import rapidjson as json
import structlog
import uvloop

from tqdm import tqdm

from sbds.storages.db.tasks import task_init_db_if_required
from sbds.storages.db.tasks import task_collect_missing_block_nums
from sbds.storages.db.tasks import task_load_account_names
from sbds.storages.db.tasks import task_add_missing_blocks


# pylint: skip-file
logger = structlog.get_logger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

TOTAL_TASKS = 7
TASK_NUM = iter(range(1, 20))


pbar_kwargs = dict(
    color=True,
    show_eta=False,
    show_percent=False,
    empty_char='░',
    fill_char='█',
    show_pos=True,
    bar_template='%(bar)s  %(info)s')


def fmt_success_message(msg, *args):
    base_msg = msg % args
    return '{success} {msg}'.format(
        success=click.style('success', fg='green'), msg=base_msg)


def fmt_task_message(task_msg,
                     emoji_code_point=None,
                     show_emoji=None,
                     total_tasks=TOTAL_TASKS):

    show_emoji = show_emoji or os.sys.platform == 'darwin'
    _emoji = ''
    if show_emoji:
        _emoji = emoji_code_point

    task_num = next(TASK_NUM)
    return '[{task_num}/{total_tasks}] {task_emoji}  {task_msg}...'.format(
        task_num=task_num,
        total_tasks=total_tasks,
        task_emoji=_emoji,
        task_msg=task_msg)


@click.command()
@click.option(
    '--database_url',
    type=str,
    envvar='DATABASE_URL',
    help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default'
)
@click.option(
    '--legacy_database_url',
    type=str,
    envvar='LEGACY_DATABASE_URL',
    help='Database connection URL in RFC-1738 format, read from "LEGACY_DATABASE_URL" ENV var by default'
)
@click.option(
    '--steemd_http_url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    help='Steemd HTTP server URL')
@click.option('--start_block', type=click.INT, default=1)
@click.option('--end_block', type=click.INT, default=-1)
@click.option('--accounts_file', type=click.Path(dir_okay=False, exists=True))
@click.option('--concurrency', type=click.INT, default=5)
@click.option('--jsonrpc_batch_size', type=click.INT, default=60)
def populate(database_url, legacy_database_url, steemd_http_url,
             start_block, end_block, accounts_file, concurrency, jsonrpc_batch_size):
    _populate(
        database_url,
        legacy_database_url,
        steemd_http_url,
        start_block,
        end_block,
        accounts_file,
        concurrency,
        jsonrpc_batch_size)


def _populate(database_url, legacy_database_url, steemd_http_url,
              start_block, end_block, accounts_file, concurrency, jsonrpc_batch_size):

        # init db if required
    task_message = fmt_task_message(
        'Initialising db if required',
        emoji_code_point=u'\U0001F50C')
    click.echo(task_message)
    task_init_db_if_required(database_url=legacy_database_url)

    # preload accounts file
    if accounts_file:
        task_message = fmt_task_message(
            'Preloading account names',
            emoji_code_point=u'\U0001F52D')
        click.echo(task_message)
        task_load_account_names(database_url=database_url,
                                accounts_file=accounts_file)
    else:
        task_message = fmt_success_message('No accounts file provided...skipping ')
        click.echo(task_message)

    # collect missing block nums
    if end_block == -1:
        end_block_msg = 'latest'
    else:
        end_block_msg = str(end_block)
    task_message = fmt_task_message(
        f'Building list of blocks missing from db between {start_block}<<-->>{end_block_msg}',
        emoji_code_point=u'\U0001F52D')
    click.echo(task_message)
    missing_exising_results = task_collect_missing_block_nums(database_url=database_url,
                                                              steemd_http_url=steemd_http_url,
                                                              start_block=start_block,
                                                              end_block=end_block)

    # add missing blocks and operations
    task_message = fmt_task_message(
        'Adding missing blocks and operations to db',
        emoji_code_point=u'\U0001F52D')
    task_add_missing_blocks(database_url=database_url,
                            steemd_http_url=steemd_http_url,
                            concurrency=concurrency,
                            num_procs=None,
                            jsonrpc_batch_size=jsonrpc_batch_size,
                            missing_block_nums=missing_exising_results['missing_block_nums'],
                            existing_count=missing_exising_results['existing_count'],
                            missing_count=missing_exising_results['missing_count'],
                            range_count=missing_exising_results['range_count'])


if __name__ == '__main__':
    populate()
