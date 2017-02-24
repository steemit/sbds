# -*- coding: utf-8 -*-
import os

import concurrent.futures
from functools import partial

from collections import namedtuple

import click
from sqlalchemy.engine.url import make_url
from steemapi.steemnoderpc import SteemNodeRPC

import sbds.sbds_json
from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session
from sbds.storages.db.tables import init_tables
from sbds.storages.db.tables import test_connection
from sbds.storages.db.tables import Block
from sbds.storages.db.utils import configure_engine
from sbds.storages.db.utils import kill_db_processes
from sbds.storages.db import bulk_add
from sbds.storages.db import add_blocks
from sbds.utils import chunkify

# pylint: skip-file
logger = sbds.sbds_logging.getLogger(__name__)
TOTAL_TASKS = 7
MAX_CHUNKSIZE = 1000000

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


def task_confirm_db_connectivity(database_url):
    # [1/7] confirm db connectivity
    task_message = fmt_task_message(
        'Confirm database connectivity',
        emoji_code_point=u'\U0001F4DE',
        task_num=1)
    click.echo(task_message)

    url, table_count = test_connection(database_url)

    if url:
        success_msg = fmt_success_message(
            'connected to %s and found %s tables', url.__repr__(), table_count)
        click.echo(success_msg)

    if not url:
        raise Exception('Unable to connect to database')


def task_kill_existing_db_threads(database_url):

    task_message = fmt_task_message(
        'Killing active db threads', emoji_code_point='\U0001F4A5', task_num=2)
    click.echo(task_message)
    url = make_url(database_url)
    if url.get_backend_name() == 'sqlite':
        return

    db_name = url.database
    db_user_name = url.username
    all_procs, killed_procs = kill_db_processes(database_url, db_name,
                                                db_user_name)
    if len(killed_procs) > 0:
        success_msg = fmt_success_message('killed %s processes',
                                          len(killed_procs))
        click.echo(success_msg)


def task_init_db_if_required(database_url):
    # [3/7] init db if required
    task_message = fmt_task_message(
        'Initialising db if required',
        emoji_code_point=u'\U0001F50C',
        task_num=3)
    click.echo(task_message)
    init_tables(database_url, Base.metadata)


def task_get_last_irreversible_block(rpc):
    # [4/7] find last irreversible block
    last_chain_block = rpc.last_irreversible_block_num()
    task_message = fmt_task_message(
        'Finding highest blockchain block',
        emoji_code_point='\U0001F50E',
        task_num=4)
    click.echo(task_message)


def task_find_missing_block_nums(database_url, last_chain_block):
    # [5/7] get missing block_nums
    task_message = fmt_task_message(
        'Finding blocks missing from db',
        emoji_code_point=u'\U0001F52D',
        task_num=5)
    click.echo(task_message)

    engine_config = configure_engine(database_url)
    session = Session(bind=engine_config.engine)

    missing_block_nums_gen = Block.get_missing_block_num_iterator(
        session, last_chain_block, chunksize=100000)

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
    session.invalidate()
    return all_missing_block_nums


def task_add_missing_blocks(all_missing_block_nums, max_procs, max_threads,
                            database_url, steemd_http_url):
    # [6/7] adding missing blocks
    task_message = fmt_task_message(
        'Adding missing blocks to db, this may take a while',
        emoji_code_point=u'\U0001F4DD',
        task_num=6)
    click.echo(task_message)

    max_workers = max_procs or os.cpu_count() or 1

    chunksize = len(all_missing_block_nums) // max_workers
    if chunksize <= 0:
        chunksize = 1

    map_func = partial(
        block_adder_process_worker,
        database_url,
        steemd_http_url,
        max_threads=max_threads)

    chunks = chunkify(all_missing_block_nums, 10000)

    with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers) as executor:
        executor.map(map_func, chunks, chunksize=1)

    success_msg = fmt_success_message('added missing blocks')
    click.echo(success_msg)


def task_stream_blocks(database_url, steemd_websocket_url):
    # [7/7] stream blocks
    task_message = fmt_task_message(
        'Streaming blocks', emoji_code_point=u'\U0001F4DD', task_num=7)
    click.echo(task_message)

    engine_config = configure_engine(database_url)
    session = Session(bind=engine_config.engine)
    highest_db_block = Block.highest_block(session)

    ws_rpc = SteemNodeRPC(steemd_websocket_url)
    blocks = ws_rpc.block_stream(highest_db_block)

    add_blocks(blocks, session)


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
@click.option(
    '--steemd_websocket_url',
    metavar='WEBSOCKET_URL',
    envvar='WEBSOCKET_URL',
    help='Steemd websocket server URL')
@click.option('--max_procs', type=click.INT, default=None)
@click.option('--max_threads', type=click.INT, default=5)
def populate(database_url, steemd_http_url, steemd_websocket_url, max_procs,
             max_threads):
    _populate(database_url, steemd_http_url, steemd_websocket_url, max_procs,
              max_threads)


def _populate(database_url, steemd_http_url, steemd_websocket_url, max_procs,
              max_threads):
    # pylint: disable=too-many-locals, too-many-statements
    rpc = SimpleSteemAPIClient(steemd_http_url)
    engine_config = configure_engine(database_url)
    session = Session(bind=engine_config.engine)

    db_name = engine_config.url.database
    db_user_name = engine_config.url.username

    Session.configure(bind=engine_config.engine)
    session = Session()

    # [1/7] confirm db connectivity
    task_message = fmt_task_message(
        'Confirm database connectivity',
        emoji_code_point=u'\U0001F4DE',
        task_num=1)
    click.echo(task_message)

    url, table_count = test_connection(database_url)
    if url:
        success_msg = fmt_success_message(
            'connected to %s and found %s tables', url.__repr__(), table_count)
        click.echo(success_msg)

    if not url:
        raise Exception('Unable to connect to database')
    del url
    del table_count

    # [2/7] kill existing db threads

    task_message = fmt_task_message(
        'Killing active db threads', emoji_code_point='\U0001F4A5', task_num=2)
    click.echo(task_message)
    all_procs, killed_procs = kill_db_processes(database_url, db_name,
                                                db_user_name)
    if len(killed_procs) > 0:
        success_msg = fmt_success_message('killed %s processes',
                                          len(killed_procs))
        click.echo(success_msg)
    del all_procs
    del killed_procs

    # [3/7] init db if required
    task_message = fmt_task_message(
        'Initialising db if required',
        emoji_code_point=u'\U0001F50C',
        task_num=3)
    click.echo(task_message)
    init_tables(database_url, Base.metadata)

    # [4/7] find last irreversible block
    last_chain_block = rpc.last_irreversible_block_num()
    task_message = fmt_task_message(
        'Finding highest blockchain block',
        emoji_code_point='\U0001F50E',
        task_num=4)
    click.echo(task_message)

    success_msg = fmt_success_message(
        'learned highest irreversible block is %s', last_chain_block)
    click.echo(success_msg)

    # [5/7] get missing block_nums
    task_message = fmt_task_message(
        'Finding blocks missing from db',
        emoji_code_point=u'\U0001F52D',
        task_num=5)
    click.echo(task_message)
    missing_block_nums_gen = Block.get_missing_block_num_iterator(
        session, last_chain_block, chunksize=100000)

    with click.progressbar(
            missing_block_nums_gen,
            label='Finding missing block_nums',
            color=True,
            show_eta=False,
            show_percent=False,
            empty_char='░',
            fill_char='█',
            show_pos=True,
            bar_template='%(bar)s  %(info)s') as pbar:
        all_missing_block_nums = []
        for missing_gen in pbar:
            all_missing_block_nums.extend(missing_gen())

    success_msg = fmt_success_message('found %s missing blocks',
                                      len(all_missing_block_nums))
    click.echo(success_msg)
    del missing_block_nums_gen
    del pbar
    session.invalidate()

    # [6/7] adding missing blocks
    task_message = fmt_task_message(
        'Adding missing blocks to db, this may take a while',
        emoji_code_point=u'\U0001F4DD',
        task_num=6)
    click.echo(task_message)

    max_workers = max_procs or os.cpu_count() or 1

    chunksize = len(all_missing_block_nums) // max_workers
    if chunksize <= 0:
        chunksize = 1

    map_func = partial(
        block_adder_process_worker,
        database_url,
        steemd_http_url,
        max_threads=max_threads)

    chunks = chunkify(all_missing_block_nums, 10000)

    with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers) as executor:
        executor.map(map_func, chunks, chunksize=1)

    success_msg = fmt_success_message('added missing blocks')
    click.echo(success_msg)
    del all_missing_block_nums

    # [7/7] stream blocks
    task_message = fmt_task_message(
        'Streaming blocks', emoji_code_point=u'\U0001F4DD', task_num=7)
    click.echo(task_message)

    highest_db_block = Block.highest_block(session)
    ws_rpc = SteemNodeRPC(steemd_websocket_url)
    blocks = ws_rpc.block_stream(highest_db_block)
    add_blocks(blocks, session)


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
    try:
        engine_config = configure_engine(database_url)
        session = Session(bind=engine_config.engine)
        raw_blocks = block_fetcher_thread_worker(
            rpc_url, block_nums, max_threads=max_threads)
        for raw_blocks_chunk in chunkify(raw_blocks, 1000):
            # pylint: disable=unused-variable
            # we could do something here with results, like retry failures
            results = bulk_add(raw_blocks_chunk, session)

    except Exception as e:
        logger.exception(e)
    finally:
        Session.close_all()


# included only for debugging with pdb, all the above code should be called
# using the click framework
if __name__ == '__main__':
    db_url = os.environ['DATABASE_URL']
    rpc_url = os.environ['STEEMD_HTTP_URL']
    ws_rpc_url = os.environ['WEBSOCKET_URL']
    _populate(
        db_url,
        rpc_url,
        steemd_websocket_url=ws_rpc_url,
        max_procs=4,
        max_threads=2)
