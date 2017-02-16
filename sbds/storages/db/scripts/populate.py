# -*- coding: utf-8 -*-
import os
import concurrent.futures
from functools import partial


import click
import click_spinner
import emoji

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
from sbds.storages.db import add_block
from sbds.utils import chunkify
from sbds.logging import generate_fail_log_from_raw_block

logger = sbds.logging.getLogger(__name__)
TOTAL_TASKS = 6


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
def populate(database_url, steemd_http_url):
    _populate(database_url, steemd_http_url)




def _populate(database_url, steemd_http_url):
    rpc = SimpleSteemAPIClient(steemd_http_url)
    engine_config = configure_engine(database_url)

    db_name = engine_config.url.database
    db_user_name = engine_config.url.username

    Session.configure(bind=engine_config.engine)
    session = Session()

    # [1/6] confirm db connectivity

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

    # [2/6] kill existing db threads

    task_message = fmt_task_message('Killing active db threads',
                                    emoji_code_point='\U0001F4A5', counter=2)
    click.echo(task_message)
    all_procs, killed_procs = kill_db_processes(database_url, db_name, db_user_name)
    if len(killed_procs) > 0:
        success_msg = fmt_success_message('killed %s processes', len(killed_procs))
        click.echo(success_msg)


    # [3/6] init db if required
    task_message = fmt_task_message('Initialising db if required',
                                    emoji_name=':electric_plug:', counter=3)
    click.echo(task_message)
    init_tables(database_url, Base.metadata)



    # [4/6] find last irreversible block
    last_chain_block = rpc.last_irreversible_block_num()
    task_message = fmt_task_message('Finding highest blockchain block',
                                    emoji_code_point='\U0001F50E', counter=4)
    click.echo(task_message)



    success_msg = fmt_success_message('learned highest irreversible block is %s',
                                      last_chain_block)
    click.echo(success_msg)


    # [5/6] get missing block_nums

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

    # [6/6] adding missing blocks

    task_message = fmt_task_message('Adding missing blocks to db',
                                    emoji_name=':memo:', counter=6)
    click.echo(task_message)

    num_chunks = os.cpu_count() or 1
    chunksize = len(all_missing_block_nums) // num_chunks


    map_func = partial(block_adder_process_worker, database_url, steemd_http_url)

    block_chunks = chunkify(all_missing_block_nums, chunksize)
    with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(map_func, block_chunks)


def block_adder_process_worker(database_url, rpc_url, block_nums):
    try:
        rpc = SimpleSteemAPIClient(rpc_url)
        engine_config = configure_engine(database_url)
        Session.configure(bind=engine_config.engine)
        session = Session()
        completed = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_raw_block = {executor.submit(rpc.get_block, block_num): block_num for block_num in block_nums}

            for future in concurrent.futures.as_completed(future_to_raw_block):
                block_num = future_to_raw_block[future]
                try:
                    raw_block = future.result()
                except Exception as e:
                   logger.error(e)
                else:
                    result = add_block(raw_block, session, insert=True, _raise=True)
                    if not result:
                        generate_fail_log_from_raw_block(logger, raw_block)

    except Exception as e:
        logger.exception(e)
    finally:
        Session.close_all()


if __name__ == '__main__':
    db_url = os.environ['DATABASE_URL']
    rpc_url = os.environ['STEEMD_HTTP_URL']
    _populate(db_url, rpc_url)