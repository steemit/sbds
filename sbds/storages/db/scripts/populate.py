# -*- coding: utf-8 -*-
import os
import concurrent.futures
from functools import partial


import click
import click_spinner
import emoji
from steemapi.steemnoderpc import SteemNodeRPC

import sbds.logging
import sbds.json
from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db import Base
from sbds.storages.db import Session
from sbds.storages.db.tables import init_tables
from sbds.storages.db.tables import test_connection
from sbds.storages.db.tables import Block
from sbds.storages.db.utils import configure_engine
from sbds.storages.db.utils import kill_db_processes
from sbds.storages.db import bulk_add
from sbds.storages.db import add_blocks
from sbds.utils import chunkify

logger = sbds.logging.getLogger(__name__)
TOTAL_TASKS = 7
MAX_CHUNKSIZE = 1000000

def fmt_success_message(msg, *args):
    base_msg = msg % (args)
    return '{success} {msg}'.format(
       success=click.style('success', fg='green'),
       msg=base_msg)


def fmt_task_message(task_msg, emoji_name=None, emoji_code_point=None,
                     show_emoji=None, counter=None):


    show_emoji = show_emoji or os.sys.platform == 'darwin'
    if show_emoji:
        if emoji_code_point:
            _emoji = emoji_code_point
        elif emoji_name:
            _emoji = emoji.emojize(emoji_name)
    else:
        _emoji = ''


    return '[{counter}/{total_tasks}] {task_emoji}  {task_msg}...'.format(
        counter=counter,
        total_tasks=TOTAL_TASKS,
        task_emoji=_emoji,
        task_msg=task_msg
    )


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
def populate(database_url, steemd_http_url, steemd_websocket_url,
             max_procs, max_threads):
    _populate(database_url, steemd_http_url, steemd_websocket_url,
              max_procs, max_threads)

def _populate(database_url, steemd_http_url, steemd_websocket_url,
              max_procs, max_threads):
    rpc = SimpleSteemAPIClient(steemd_http_url)
    engine_config = configure_engine(database_url)

    db_name = engine_config.url.database
    db_user_name = engine_config.url.username

    Session.configure(bind=engine_config.engine)
    session = Session()

    # [1/7] confirm db connectivity

    task_message = fmt_task_message('Confirm database connectivity',
                                    emoji_name=':telephone_receiver:',
                                    counter=1)
    click.echo(task_message)


    url, table_count = test_connection(database_url)
    if url:
        success_msg = fmt_success_message('connected to %s and found %s tables',
            url.__repr__(), table_count)
        click.echo(success_msg)
    if not url:
        click.fail('Unable to connect to database')

    # [2/7] kill existing db threads

    task_message = fmt_task_message('Killing active db threads',
                                    emoji_code_point='\U0001F4A5', counter=2)
    click.echo(task_message)
    all_procs, killed_procs = kill_db_processes(database_url, db_name, db_user_name)
    if len(killed_procs) > 0:
        success_msg = fmt_success_message('killed %s processes', len(killed_procs))
        click.echo(success_msg)


    # [3/7] init db if required
    task_message = fmt_task_message('Initialising db if required',
                                    emoji_name=':electric_plug:', counter=3)
    click.echo(task_message)
    init_tables(database_url, Base.metadata)



    # [4/7] find last irreversible block
    last_chain_block = rpc.last_irreversible_block_num()
    task_message = fmt_task_message('Finding highest blockchain block',
                                    emoji_code_point='\U0001F50E', counter=4)
    click.echo(task_message)



    success_msg = fmt_success_message('learned highest irreversible block is %s',
                                      last_chain_block)
    click.echo(success_msg)


    # [5/7] get missing block_nums

    _chunksize = 100000
    missing_block_nums_gen = Block.get_missing_block_num_iterator(
        session, last_chain_block, chunksize=_chunksize)

    task_message = fmt_task_message('Finding blocks missing from db',
                                    emoji_name=':telescope:', counter=5)
    click.echo(task_message)

    with click.progressbar(missing_block_nums_gen,
                           label='Finding missing block_nums',
                           color=True,
                           show_eta=False,
                           show_percent=False,
                           empty_char='░',
                           fill_char='█',
                           show_pos=True,
                           bar_template='%(bar)s  %(info)s') as bar:
        all_missing_block_nums = []
        for missing_gen in bar:
            all_missing_block_nums.extend(missing_gen())

    success_msg = fmt_success_message('found %s missing blocks',
        len(all_missing_block_nums))
    click.echo(success_msg)

    # [6/7] adding missing blocks

    task_message = fmt_task_message('Adding missing blocks to db, this may take a while',
                                    emoji_name=':memo:', counter=6)
    click.echo(task_message)

    max_workers = max_procs or os.cpu_count() or 1
    num_chunks = max_workers
    chunksize = len(all_missing_block_nums) // num_chunks
    if chunksize <= 0:
        chunksize = 1
    if chunksize > MAX_CHUNKSIZE:
        chunksize = MAX_CHUNKSIZE

    map_func = partial(block_adder_process_worker, database_url,
                       steemd_http_url, max_threads=max_threads)

    block_chunks = chunkify(all_missing_block_nums, chunksize)
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            executor.map(map_func, block_chunks, chunksize=chunksize)

    success_msg = fmt_success_message('added missing blocks')
    click.echo(success_msg)

    # [7/7] stream blocks
    task_message = fmt_task_message('Streaming blocks',
                                    emoji_name=':memo:',
                                    counter=7)
    click.echo(task_message)

    highest_db_block = Block.highest_block(session)
    ws_rpc = SteemNodeRPC(steemd_websocket_url)
    blocks = ws_rpc.block_stream(highest_db_block)
    add_blocks(blocks, session)


def block_fetcher_thread_worker(rpc_url, block_nums, max_threads=None):
    rpc = SimpleSteemAPIClient(rpc_url, return_with_args=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        for result, args in executor.map(rpc.get_block, block_nums):
                # dont yield anything when we encounter a null output
                # from an HTTP 503 error
                if result:
                    yield result


def block_adder_process_worker(database_url, rpc_url, block_nums, max_threads=5):
    try:
        engine_config = configure_engine(database_url)
        session = Session(bind=engine_config.engine)
        raw_blocks = block_fetcher_thread_worker(rpc_url, block_nums,
                                                 max_threads=max_threads)
        for raw_blocks_chunk in chunkify(raw_blocks, 1000):
            result = bulk_add(raw_blocks_chunk, session)
            # we could do something here with results like retry or queue failures
    except Exception as e:
        logger.exception(e)
    finally:
        Session.close_all()

# included only for debugging with pdb
if __name__ == '__main__':
    db_url = os.environ['DATABASE_URL']
    rpc_url = os.environ['STEEMD_HTTP_URL']
    ws_rpc_url = os.environ['WEBSOCKET_URL']
    _populate(db_url, rpc_url, steemd_websocket_url=ws_rpc_url, max_procs=1, max_threads=1)