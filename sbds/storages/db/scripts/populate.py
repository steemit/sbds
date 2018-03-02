# -*- coding: utf-8 -*-
import asyncio
import os
import functools
import aiopg.sa
import click
import sys
import logging
from asyncio import Queue

import uvloop
from tqdm import tqdm
import psycopg2

import jsonrpcclient.config
from sqlalchemy.engine.url import make_url
import rapidjson as json
import structlog
import aiohttp
from aiohttp.connector import TCPConnector
from jsonrpcclient.http_client import HTTPClient


from sbds.storages.db import add_blocks
from sbds.storages.db.tables.async_core import prepare_raw_block_for_storage
from sbds.storages.db.tables.operations import op_db_table_for_type
from sbds.storages.db.tables.async_core import prepare_raw_opertaion_for_storage
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

stored_blocks_q = Queue(loop=loop)


pbar_kwargs = dict(
    color=True,
    show_eta=False,
    show_percent=False,
    empty_char='░',
    fill_char='█',
    show_pos=True,
    bar_template='%(bar)s  %(info)s')

jsonrpcclient.config.validate = False


def create_async_engine(database_url, **kwargs):
    sa_db_url = make_url(database_url)
    loop = asyncio.get_event_loop()
    async_engine = loop.run_until_complete(
        aiopg.sa.create_engine(
            user=sa_db_url.username,
            password=sa_db_url.password,
            host=sa_db_url.host,
            port=sa_db_url.port,
            dbname=sa_db_url.database,
            minsize=30,
            maxsize=30,
            **kwargs))
    return async_engine


def create_async_pool(database_url, **kwargs):
    sa_db_url = make_url(database_url)
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(
        aiopg.create_pool(
            loop=loop,
            host=sa_db_url.host,
            user=sa_db_url.username,
            password=sa_db_url.password,
            dbname=sa_db_url.database,

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


def task_confirm_db_connectivity(database_url):
    url, table_count = test_connection(database_url)

    if url:
        success_msg = fmt_success_message(
            'connected to %s and found %s tables', url.__repr__(), table_count)
        click.echo(success_msg)

    if not url:
        raise Exception('Unable to connect to database')


def task_init_db_if_required(database_url):

    init_tables(database_url, Base.metadata)


def task_load_db_meta(database_url):
    with isolated_engine(db_url) as engine:
        from sqlalchemy import MetaData
        m = MetaData()
        m.reflect(bind=engine)
    return m


def task_get_last_irreversible_block(steemd_http_url):
    rpc = HTTPClient(steemd_http_url)
    rpc._request_log.level = 50
    rpc._response_log.level = 50
    response = rpc.request('get_dynamic_global_properties')
    last_chain_block = response['last_irreversible_block_num']
    return last_chain_block


async def get_missing_count(engine, last_chain_block,):
    async with engine.acquire() as conn:
        existing_count = await conn.scalar('SELECT COUNT(*) from sbds_core_blocks')
    missing_count = last_chain_block - existing_count
    return missing_count


async def enqueue_missing_block_nums(engine, last_chain_block, missing_count, pbar=None):
    complete_block_nums = range(1, last_chain_block + 1)
    if missing_count == last_chain_block:
        return complete_block_nums
    missing_block_nums = list()
    async with engine.acquire() as conn:

        for complete_block_num_chunk in chunkify(complete_block_nums, 10_000):
            complete_block_num_chunk = list(complete_block_num_chunk)
            low = min(complete_block_num_chunk)
            high = max(complete_block_num_chunk)
            rows = await conn.execute(
                f'SELECT block_num from sbds_core_blocks WHERE block_num>={low} AND block_num<{high} ORDER BY block_num ASC ')
            block_nums_in_db_chunk = await rows.fetchall()
            if block_nums_in_db_chunk:
                block_nums_in_db_chunk = [b[0] for b in block_nums_in_db_chunk]
                missing_in_chunk = set(complete_block_num_chunk)
                missing_in_chunk.difference_update(set(block_nums_in_db_chunk))
                if missing_in_chunk:
                    missing_block_nums.extend(missing_in_chunk)
                pbar.update(10_000)
            else:
                missing_block_nums.extend(complete_block_num_chunk)
                pbar.update(10_000)

    return missing_block_nums


async def fetch_block(url, client, block_num):
    response = await client.post(url, data=f'{{"id":{block_num},"jsonrpc":"2.0","method":"get_block","params":[{block_num}]}}'.encode())
    jsonrpc_response = await response.json()
    return jsonrpc_response['result']


async def fetch_blocks(url, client, block_nums):
    request_data = ','.join(
        f'{{"id":{block_num},"jsonrpc":"2.0","method":"get_block","params":[{block_num}]}}' for block_num in block_nums)
    request_json = f'[{request_data}]'.encode()
    response = await client.post(url, data=request_json)
    jsonrpc_response = await response.json()
    return zip(block_nums, [r['result'] for r in jsonrpc_response])


async def store_block(engine, db_tables, prepared_block, pbar=None):
    blocks_table = db_tables['sbds_core_blocks']
    accounts_table = db_tables['sbds_meta_accounts']
    async with engine.acquire() as conn:
        while True:
            try:
                await conn.execute(blocks_table.insert().values(**prepared_block))
                if pbar:
                    pbar.update(1)
                break
            except psycopg2.IntegrityError as e:
                # Key (worker_account)=(kevtorin) is not present in table "sbds_meta_accounts"
                err_str = e.diag.message_detail
                if 'is not present in table "sbds_meta_accounts"' in err_str:
                    missing_account_name = err_str.split('=')[1].split(')')[
                        0].replace('(', '')  # hehe
                    try:
                        await conn.execute(accounts_table.insert().values(
                            name=missing_account_name))
                    except psycopg2.IntegrityError as e:
                        if 'duplicate key value violates unique constraint' in e.pgerror:
                            pass
                        else:
                            raise e
                else:
                    raise e


async def process_block(block_num, url, client, engine, db_tables, pbar=None):
    raw_block = await fetch_block(url, client, block_num)
    prepared_block = await prepare_raw_block_for_storage(raw_block, loop=loop)
    await store_block(engine, db_tables, prepared_block, pbar=pbar)
    return (block_num, raw_block, prepared_block)


async def process_blocks(missing_block_nums, url, client, engine, db_meta, pbar=None):
    db_tables = db_meta.tables
    for block_num_chunk in chunkify(missing_block_nums, 150):
        request_tasks = [
            process_block(
                block_num,
                url,
                client,
                engine,
                db_tables,
                pbar=pbar) for block_num,
            raw_block in block_num_chunk]
        done, pending = await asyncio.wait(request_tasks)
        for task in done:
            try:
                result = task.result()
                stored_blocks_q.put_nowait(result)
                pbar.update(1)
            except Exception as e:
                logger.error('task error', e=e, task=task)


async def process_block2(block_num, raw_block, url, client, engine, db_tables, pbar=None):
    prepared_block = await prepare_raw_block_for_storage(raw_block, loop=loop)
    await store_block(engine, db_tables, prepared_block, pbar=pbar)
    return (block_num, raw_block, prepared_block)


async def process_blocks2(missing_block_nums, url, client, engine, db_meta, pbar=None):
    db_tables = db_meta.tables
    for block_num_chunk in chunkify(missing_block_nums, 500):
        results = await fetch_blocks(url, client, block_num_chunk)
        request_tasks = [
            process_block2(
                block_num,
                raw_block,
                url,
                client,
                engine,
                db_tables,
                pbar=pbar) for block_num,
            raw_block in results]
        done, pending = await asyncio.wait(request_tasks)
        for task in done:
            try:
                result = task.result()
                stored_blocks_q.put_nowait(result)
                pbar.update(1)
            except Exception as e:
                logger.error('task error', e=e, task=task)


# --- Operations ---
async def fetch_ops_in_block(url, client, block_num):
    response = await client.post(url, data=f'{{"id":{block_num},"jsonrpc":"2.0","method":"get_ops_in_block","params":[{block_num},false]}}'.encode())
    jsonrpc_response = await response.json()
    return jsonrpc_response['result']


async def fetch_ops_in_blocks(url, client, block_nums):
    request_data = ','.join(
        f'{{"id":{block_num},"jsonrpc":"2.0","method":"get_ops_in_block","params":[{block_num},false]}}' for block_num in block_nums)
    request_json = f'[{request_data}]'.encode()
    response = await client.post(url, data=request_json)
    jsonrpc_response = await response.json()
    return zip(block_nums, [r['result'] for r in jsonrpc_response])


async def prepare_operation_for_storage(raw_operation):
    try:
        return await prepare_raw_opertaion_for_storage(raw_operation)
    except Exception as e:
        logger.error('prepare_operation_for_storage', raw_operation=raw_operation, e=e)
        raise e


async def store_operation(engine, db_tables, prepared_operation, pbar=None):
    try:
        table_name = op_db_table_for_type(prepared_operation['operation_type'])
        accounts_table = db_tables['sbds_meta_accounts']
        table = db_tables[table_name]
        async with engine.acquire() as conn:
            while True:
                try:
                    await conn.execute(table.insert().values(**prepared_operation))
                    break
                except psycopg2.IntegrityError as e:
                    # Key (worker_account)=(kevtorin) is not present in table "sbds_meta_accounts"
                    err_str = e.diag.message_detail
                    if 'is not present in table "sbds_meta_accounts"' in err_str:
                        missing_account_name = err_str.split(
                            '=')[1].split(')')[0].replace('(', '')  # hehe
                        try:
                            await conn.execute(accounts_table.insert().values(name=missing_account_name))
                        except psycopg2.IntegrityError as e:
                            if 'duplicate key value violates unique constraint' in e.pgerror:
                                pass
                            else:
                                raise e
                    else:
                        raise e
    except Exception as e:
        logger.error('store_operation', prepared_operation=prepared_operation, e=e)
        raise e


async def process_operation(block_num, url, client, engine, db_tables, pbar=None):
    raw_operations = await fetch_ops_in_block(url, client, block_num)
    for raw_operation in raw_operations:
        try:
            prepared_operation = await prepare_raw_opertaion_for_storage(raw_operation, loop=loop)
            await store_operation(engine, db_tables, prepared_operation, pbar=pbar)
        except Exception as e:
            logger.error('process_operation',
                         raw_operation=raw_operation,
                         e=e)
            raise e


async def process_operations(stored_blocks_q, url, client, engine, db_meta, pbar=None):
    db_tables = db_meta.tables
    block_num_chunk = []
    while True:
        try:
            block_num, raw_block, prepared_block = stored_blocks_q.get_nowait()
        except asyncio.QueueEmpty:
            await asyncio.sleep(1)
            continue
        block_num_chunk.append(block_num)
        if len(block_num_chunk) >= 100:
            tasks = [
                process_operation(
                    block_num,
                    url,
                    client,
                    engine,
                    db_tables,
                    pbar=pbar) for block_num in block_num_chunk]
            done, pending = await asyncio.wait(tasks)
            for task in done:
                try:
                    result = task.result()
                    if pbar:
                        pbar.update(1)
                except Exception as e:
                    logger.error('task error', e=e, task=task, exc_info=e)
            block_num_chunk = []


async def process_operation2(block_num, raw_operations, url, client, engine, db_tables, pbar=None):
    for raw_operation in raw_operations:
        try:
            prepared_operation = await prepare_raw_opertaion_for_storage(raw_operation, loop=loop)
            await store_operation(engine, db_tables, prepared_operation, pbar=pbar)
        except Exception as e:
            logger.error('process_operation',
                         raw_operation=raw_operation,
                         e=e)
            raise e


async def process_operations2(stored_blocks_q, url, client, engine, db_meta, pbar=None):
    db_tables = db_meta.tables
    block_num_chunk = []
    while True:
        try:
            block_num, raw_block, prepared_block = stored_blocks_q.get_nowait()
        except asyncio.QueueEmpty:
            await asyncio.sleep(1)
            continue
        block_num_chunk.append(block_num)
        if len(block_num_chunk) >= 300:
            results = await fetch_ops_in_blocks(url, client, block_num_chunk)
            tasks = [
                process_operation2(
                    block_num,
                    raw_operations,
                    url,
                    client,
                    engine,
                    db_tables,
                    pbar=pbar) for block_num,
                raw_operations in results]
            done, pending = await asyncio.wait(tasks)
            for task in done:
                try:
                    result = task.result()
                    if pbar:
                        pbar.update(1)
                except Exception as e:
                    logger.error('task error', e=e, task=task, exc_info=e)
            block_num_chunk = []


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
    connector = TCPConnector(loop=loop, limit=200)
    AIOHTTP_SESSION = aiohttp.ClientSession(loop=loop,
                                            connector=connector,
                                            json_serialize=json.dumps,
                                            headers={'Content-Type': 'application/json'})

    try:
        engine = create_async_engine(database_url)
        task_num = 0
        # [1/6] confirm db connectivity
        task_num += 1
        task_message = fmt_task_message(
            'Confirm database connectivity',
            emoji_code_point=u'\U0001F4DE',
            task_num=task_num)
        click.echo(task_message)
        task_confirm_db_connectivity(database_url)

        # [2/6] init db if required
        task_num += 1
        task_message = fmt_task_message(
            'Initialising db if required',
            emoji_code_point=u'\U0001F50C',
            task_num=task_num)
        click.echo(task_message)
        task_init_db_if_required(database_url=database_url)

        # [3/6] find last irreversible block
        task_num += 1
        task_message = fmt_task_message(
            'Finding highest blockchain block',
            emoji_code_point='\U0001F50E',
            task_num=task_num)
        click.echo(task_message)
        last_chain_block = task_get_last_irreversible_block(steemd_http_url)

        # [4/6] build list of blocks missing from db
        missing_count = loop.run_until_complete(get_missing_count(engine, last_chain_block))
        task_message = fmt_task_message(
            'Building list of blocks missing from db',
            emoji_code_point=u'\U0001F52D',
            task_num=4)
        click.echo(task_message)
        with click.progressbar(length=missing_count, **pbar_kwargs) as pbar:
            missing_block_nums = loop.run_until_complete(
                enqueue_missing_block_nums(
                    engine, last_chain_block, missing_count, pbar=pbar))

        task_message = fmt_task_message(
            'Adding missing blocks to db',
            emoji_code_point=u'\U0001F52D',
            task_num=5)
        click.echo(task_message)

        db_meta = task_load_db_meta(database_url)

        pbar = tqdm(total=missing_count, unit='blocks', bar_format='''{bar}{r_bar}''')
        #pbar2 = tqdm(total=missing_count,unit='blocks',bar_format='''{bar}{r_bar}''')
        asyncio.ensure_future(process_blocks2(missing_block_nums,
                                              steemd_http_url,
                                              AIOHTTP_SESSION,
                                              engine,
                                              db_meta,
                                              pbar=pbar))
        #'''
        asyncio.ensure_future(process_operations2(stored_blocks_q,
                                                  steemd_http_url,
                                                  AIOHTTP_SESSION,
                                                  engine,
                                                  db_meta,
                                                  pbar=None))
        #'''
        loop.run_forever()

        # [5/6] stream new blocks

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception('ERROR')
        raise e


# included only for debugging with pdb, all the above code should be called
# using the click framework
if __name__ == '__main__':
    db_url = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://user:password@localhost/sbds')
    rpc_url = os.environ.get('STEEMD_HTTP_URL', 'https://api.steemit.com')
    _populate(db_url, rpc_url, jsonrpc_batch_size=100)
