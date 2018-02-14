# -*- coding: utf-8 -*-
import asyncio
import os

import aiomysql.sa
import click
import janus
import uvloop
from sqlalchemy.engine.url import make_url

import structlog
from sbds.async_http_client import AsyncClient
from sbds.http_client import SimpleSteemAPIClient
from sbds.storages.db import add_blocks
from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session
from sbds.storages.db.tables import init_tables
from sbds.storages.db.tables import test_connection
from sbds.storages.db.tables.block import Block
from sbds.storages.db.utils import isolated_engine
from sbds.utils import chunkify

# pylint: skip-file
logger = structlog.get_logger(__name__)

TOTAL_TASKS = 6

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

missing_blocks_q = janus.Queue(loop=loop)
fetched_blocks_q = janus.Queue(loop=loop)
fetched_ops_q = janus.Queue(loop=loop)

progress_bar_kwargs = dict(
    color=True,
    show_eta=False,
    show_percent=False,
    empty_char='░',
    fill_char='█',
    show_pos=True,
    bar_template='%(bar)s  %(info)s')


def create_async_engine(database_url, **kwargs):
    sa_db_url = make_url(database_url)
    loop = asyncio.get_event_loop()
    async_engine = loop.run_until_complete(
        aiomysql.sa.create_engine(
            user=sa_db_url.username,
            password=sa_db_url.password,
            host=sa_db_url.host,
            port=sa_db_url.port,
            db=sa_db_url.database,
            charset='utf8mb4',
            **kwargs))
    return async_engine


def create_async_pool(database_url, **kwargs):
    sa_db_url = make_url(database_url)
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(
        aiomysql.create_pool(
            loop=loop,
            host=sa_db_url.host,
            user=sa_db_url.username,
            password=sa_db_url.password,
            db=sa_db_url.database,
            charset='utf8mb4',
            **kwargs))
    return pool


def create_async_connection(database_url, **kwargs):
    sa_db_url = make_url(database_url)
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(
        aiomysql.connect(
            loop=loop,
            host=sa_db_url.host,
            user=sa_db_url.username,
            password=sa_db_url.password,
            db=sa_db_url.database,
            charset='utf8mb4',
            **kwargs))
    return pool


def fmt_success_message(msg, *args):
    base_msg = msg % args
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


async def enqueue_missing_block_nums(database_url, last_chain_block):
    connection = create_async_connection(
        database_url, cursorclass=aiomysql.SSCursor)
    async_client = AsyncClient()

    with connection.cursor() as cursor:
        existing_count = asyncio.ensure_future(
            cursor.execute('SELECT COUNT(timestamp) from sbds_core_blocks')
            .fetchone())

    with connection.cursor() as cursor:
        missing_count = last_chain_block - existing_count

    with click.progressbar(
            length=missing_count,
            label='Finding missing block_nums',
            **progress_bar_kwargs) as pbar:

        with connection.cursor() as cursor:
            cursor.execute('SELECT block_num from sbds_core_blocks')
            existing_block_nums = cursor.fetchall()
            complete_block_nums = iter(range(1, last_chain_block + 1))
            next_block_num = 1
            missing_blocks = []
            try:
                next_existing_block_num = next(existing_block_nums)
                for next_block_num in complete_block_nums:
                    while next_existing_block_num > next_block_num:
                        missing_blocks.append(next_block_num)
                        next_block_num = next(complete_block_nums)
                    next_existing_block_num = next(existing_block_nums)
                    if len(missing_blocks) >= 150:
                        asyncio.ensure_future(
                            async_client.get_blocks(missing_blocks,
                                                    fetched_blocks_q))
                        asyncio.ensure_future(
                            add_blocks_from_q(fetched_blocks_q))
                        missing_blocks = []

            except StopIteration:
                for chunk in chunkify(missing_blocks, 150):
                    asyncio.ensure_future(
                        async_client.get_blocks(chunk, fetched_blocks_q))
                    asyncio.ensure_future(add_blocks_from_q(fetched_blocks_q))
                for chunk in chunkify(
                        range(next_block_num, last_chain_block + 1)):
                    asyncio.ensure_future(
                        async_client.get_blocks(chunk, fetched_blocks_q))
                    asyncio.ensure_future(add_blocks_from_q(fetched_blocks_q))


def task_find_missing_block_nums(database_url, last_chain_block, task_num=4):
    task_message = fmt_task_message(
        'Finding blocks missing from db',
        emoji_code_point=u'\U0001F52D',
        task_num=task_num)
    click.echo(task_message)
    connection = create_async_connection(
        database_url, cursorclass=aiomysql.SSCursor)
    async_client = AsyncClient()
    missing_block_nums = []

    with connection.cursor() as cursor:
        cursor.execute('SELECT block_num from sbds_core_blocks')

        existing_block_nums = cursor.fetchall()
        for bn in range(1, last_chain_block + 1):
            next_existing_block_num = 0
            try:
                while bn > next_existing_block_num:
                    next_existing_block_num = next(existing_block_nums)

                    if len(missing_block_nums) >= 150:
                        asyncio.ensure_future(
                            async_client.get_blocks(missing_block_nums,
                                                    fetched_blocks_q))
                    asyncio.ensure_future(add_blocks_from_q(fetched_blocks_q))

            except StopIteration:
                pass

        success_msg = fmt_success_message('completed adding missing blocks')
        click.echo(success_msg)


async def add_blocks_from_q(q):
    try:
        while True:
            block = await q.async_q.get_nowait()
            print(block)
    except asyncio.QueueEmpty:
        pass


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
                add_blocks(blocks_to_add, session, insert=True)
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
@click.option('--jsonrpc_batch_size', type=click.INT, default=100)
def populate(database_url, steemd_http_url, jsonrpc_batch_size):
    _populate(database_url, steemd_http_url, jsonrpc_batch_size)


def _populate(database_url, steemd_http_url, jsonrpc_batch_size):
    try:
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

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception('ERROR')
        raise e


# included only for debugging with pdb, all the above code should be called
# using the click framework
if __name__ == '__main__':
    db_url = os.environ['DATABASE_URL']
    rpc_url = os.environ['STEEMD_HTTP_URL']
    _populate(db_url, rpc_url, jsonrpc_batch_size=100)
