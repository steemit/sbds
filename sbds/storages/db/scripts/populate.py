# -*- coding: utf-8 -*-
import os
import atexit

import concurrent.futures
from functools import partial

from collections import namedtuple

import click
from sqlalchemy.engine.url import make_url


import sbds.sbds_json
import sbds.sbds_logging
from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session
from sbds.storages.db.tables import init_tables
from sbds.storages.db.tables import test_connection
from sbds.storages.db.tables import Block
from sbds.storages.db.utils import configure_engine
from sbds.storages.db.utils import isolated_engine
from sbds.storages.db.utils import kill_db_processes
from sbds.storages.db import bulk_add
from sbds.storages.db import add_block
from sbds.storages.db import add_blocks
from sbds.utils import chunkify

# pylint: skip-file
logger = sbds.sbds_logging.getLogger(__name__)
TOTAL_TASKS = 6
MAX_CHUNKSIZE = 1000000

# set up for clean exit



progress_bar_kwargs = dict(
    color=True,
    show_eta=False,
    show_percent=False,
    empty_char='░',
    fill_char='█',
    show_pos=True,
    bar_template='%(bar)s  %(info)s')


def fmt_success_message(msg, *args):
    base_msg = msg % (args)
    return '{success} {msg}'.format(
        success=click.style('success', fg='green'), msg=base_msg)


def fmt_task_message(task_msg,
                     emoji_code_point=None,
                     show_emoji=None,
                     task_num=None,
                     total_tasks=TOTAL_TASKS):

    show_emoji = show_emoji or os.sys.platform == 'darwin'
    _emoji = ''
    if show_emoji:
        _emoji = emoji_code_point

    return '[{task_num}/{total_tasks}] {task_emoji}  {task_msg}...'.format(
        task_num=task_num,
        total_tasks=total_tasks,
        task_emoji=_emoji,
        task_msg=task_msg)


def task_confirm_db_connectivity(database_url, task_num=1):
    task_message = fmt_task_message(
        'Confirm database connectivity',
        emoji_code_point=u'\U0001F4DE',
        task_num=task_num)
    click.echo(task_message)

    url, table_count = test_connection(database_url)

    if url:
        success_msg = fmt_success_message(
            'connected to %s and found %s tables', url.__repr__(), table_count)
        click.echo(success_msg)

    if not url:
        raise Exception('Unable to connect to database')


def task_init_db_if_required(database_url, task_num=2):
    task_message = fmt_task_message(
        'Initialising db if required',
        emoji_code_point=u'\U0001F50C',
        task_num=task_num)
    click.echo(task_message)
    init_tables(database_url, Base.metadata)


def task_get_last_irreversible_block(steemd_http_url, task_num=3):
    rpc = SimpleSteemAPIClient(steemd_http_url)
    last_chain_block = rpc.last_irreversible_block_num()
    task_message = fmt_task_message(
        'Finding highest blockchain block',
        emoji_code_point='\U0001F50E',
        task_num=task_num)
    click.echo(task_message)
    return last_chain_block


def task_find_missing_block_nums(database_url, last_chain_block, task_num=4):
    task_message = fmt_task_message(
        'Finding blocks missing from db',
        emoji_code_point=u'\U0001F52D',
        task_num=task_num)
    click.echo(task_message)
    with isolated_engine(database_url) as engine:

        session = Session(bind=engine)

        missing_block_nums_gen = Block.get_missing_block_num_iterator(
            session, last_chain_block, chunksize=1000000)

        with click.progressbar(
                missing_block_nums_gen,
                label='Finding missing block_nums',
                **progress_bar_kwargs) as pbar:

            all_missing_block_nums = []
            for missing_gen in pbar:
                all_missing_block_nums.extend(missing_gen())

        success_msg = fmt_success_message('found %s missing blocks',
                                          len(all_missing_block_nums))
        click.echo(success_msg)
    return all_missing_block_nums


def task_add_missing_blocks(missing_block_nums,
                            max_procs,
                            max_threads,
                            database_url,
                            steemd_http_url,
                            task_num=5):
    task_message = fmt_task_message(
        'Adding missing blocks to db, this may take a while',
        emoji_code_point=u'\U0001F4DD',
        task_num=task_num)
    click.echo(task_message)

    max_workers = max_procs or os.cpu_count() or 1

    chunksize = len(missing_block_nums) // max_workers
    if chunksize <= 0:
        chunksize = 1

    map_func = partial(
        block_adder_process_worker,
        database_url,
        steemd_http_url,
        max_threads=max_threads)

    chunks = chunkify(missing_block_nums, 10000)

    with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers) as executor:
        executor.map(map_func, chunks, chunksize=1)

    success_msg = fmt_success_message('added missing blocks')
    click.echo(success_msg)


def task_stream_blocks(database_url, steemd_http_url, task_num=6):
    task_message = fmt_task_message(
        'Streaming blocks', emoji_code_point=u'\U0001F4DD', task_num=task_num)
    click.echo(task_message)
    with isolated_engine(database_url, pool_recycle=3600) as engine:
        session = Session(bind=engine)
        highest_db_block = Block.highest_block(session)
        rpc = SimpleSteemAPIClient(steemd_http_url)
        blocks = rpc.stream(highest_db_block)
        blocks_to_add = []
        for block in blocks:
            try:
                blocks_to_add.append(block)
                add_blocks(blocks_to_add, session)
            except Exception as e:
                logger.exception('failed to add block')
            else:
                blocks_to_add = []


@click.command()
@click.option(
    '--database_url',
    type=str,
    envvar='DATABASE_URL',
    help='Database connection URL in RFC-1738 format, read from "DATABASE_URL" ENV var by default'
)
@click.option(
    '--steemd_http_url',
    metavar='STEEMD_HTTP_URL',
    envvar='STEEMD_HTTP_URL',
    help='Steemd HTTP server URL')
@click.option('--max_procs', type=click.INT, default=None)
@click.option('--max_threads', type=click.INT, default=5)
def populate(database_url, steemd_http_url,  max_procs, max_threads):
    _populate(database_url, steemd_http_url, max_procs, max_threads)


def _populate(database_url, steemd_http_url,  max_procs, max_threads):

    # [1/6] confirm db connectivity
    task_confirm_db_connectivity(database_url, task_num=1)

    # [2/6] init db if required
    task_init_db_if_required(database_url=database_url, task_num=2)

    # [3/6] find last irreversible block
    last_chain_block = task_get_last_irreversible_block(
        steemd_http_url, task_num=3)

    # [4/6] get missing block_nums
    missing_block_nums = task_find_missing_block_nums(
        database_url, last_chain_block, task_num=4)

    # [5/6] adding missing blocks
    task_add_missing_blocks(
        missing_block_nums,
        max_procs,
        max_threads,
        database_url,
        steemd_http_url,
        task_num=5)

    # [6/6] stream blocks
    task_stream_blocks(database_url, steemd_http_url, task_num=6)


# pylint: disable=redefined-outer-name
def block_fetcher_thread_worker(rpc_url, block_nums, max_threads=None):
    rpc = SimpleSteemAPIClient(rpc_url, return_with_args=True)
    # pylint: disable=unused-variable
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_threads) as executor:
        for result, args in executor.map(rpc.get_block, block_nums):
            # dont yield anything when we encounter a null output
            # from an HTTP 503 error
            if result:
                yield result


def block_adder_process_worker(database_url,
                               rpc_url,
                               block_nums,
                               max_threads=5):
    with isolated_engine(database_url) as engine:
        session = Session(bind=engine)
        raw_blocks = block_fetcher_thread_worker(
            rpc_url, block_nums, max_threads=max_threads)
        for raw_blocks_chunk in chunkify(raw_blocks, 1000):
            # pylint: disable=unused-variable
            # we could do something here with results, like retry failures
            results = bulk_add(raw_blocks_chunk, session)


# included only for debugging with pdb, all the above code should be called
# using the click framework
if __name__ == '__main__':
    db_url = os.environ['DATABASE_URL']
    rpc_url = os.environ['STEEMD_HTTP_URL']
    _populate(
        db_url,
        rpc_url,
        max_procs=4,
        max_threads=2)
