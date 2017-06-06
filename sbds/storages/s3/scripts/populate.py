#!/usr/bin/env python3
import argparse
import asyncio
import os
import time
import concurrent.futures
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
import functools
import itertools

import botocore.session

import ujson
import aiofiles

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']
S3_BLOCKS_BUCKET = os.environ['S3_BLOCKS_BUCKET']


def block_num_from_hash(block_hash: str) -> int:
    """
    return the first 4 bytes (8 hex digits) of the block ID (the block_num)
    Args:
        block_hash (str):

    Returns:
        int:
    """
    return int(str(block_hash)[:8], base=16)


def block_num_from_previous(previous_block_hash: str) -> int:
    """

    Args:
        previous_block_hash (str):

    Returns:
        int:
    """
    return block_num_from_hash(previous_block_hash) + 1

def block_num_key(block_num):
    return '/'.join([str(block_num), 'block.json'])

def load_json_block(raw_block):
    if isinstance(raw_block, str):
        block_dict = ujson.loads(raw_block)
        raw_block = raw_block.encode()
    elif isinstance(raw_block, bytes):
        block_dict = ujson.loads(raw_block.decode())
    elif isinstance(raw_block, dict):
        block_dict = raw_block
        raw_block = ujson.dumps(raw_block).encode()
    else:
        raise ValueError('block must be str, bytes, or dict')
    block_num = block_num_from_previous(block_dict['previous'])
    key = block_num_key(block_num)
    return raw_block, key

def chunkify(iterable, chunksize=10000):
    i = 0
    chunk = []
    for item in iterable:
        chunk.append(item)
        i += 1
        if i == chunksize:
            yield chunk
            i = 0
            chunk = []
    if len(chunk) > 0:
        yield chunk


def upload_blocks(bucket, chunk_size, max_threads, lines):
    session = botocore.session.get_session()
    client = session.create_client('s3')
    start = time.perf_counter()
    futures = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Start the load operations and mark each future with its URL
        for line in lines:
            raw_block, key = load_json_block(line)
            futures.append(executor.submit(client.put_object,Bucket=bucket,
                                 Key=key,
                                 Body=raw_block,
                                 ContentEncoding='UTF-8',
                                 ContentType='application/json'))
        end = time.perf_counter()

    done, pending = concurrent.futures.wait(futures)
    complete = time.perf_counter()
    rate = 1 / ((complete - start) / len(done))
    return len(done), int(rate)


def report_progress(counter, avg_chunk_rate,avg_actual, overhead):
    print('blocks\t\t%s\nchunk rate\t%s\nactual rate\t%s\noverhead\t%s %%\n\n' % (
        counter, avg_chunk_rate, avg_actual, overhead))

def populate(filename, max_workers, max_threads, chunk_size, bucket=S3_BLOCKS_BUCKET):
    with open(filename, mode='r') as f:
        chunks = chunkify(f, chunksize=chunk_size)
        start = time.perf_counter()
        func = functools.partial(upload_blocks, bucket, chunk_size, max_threads)
        counter = 0
        samples = 20
        chunk_rates = deque(maxlen=samples)
        actual_rates = deque(maxlen=samples)
        overheads = deque(maxlen=samples)
        with Pool(processes=max_workers) as pool:
            results = pool.imap_unordered(func, chunks, chunksize=1)
            for count, rate in results:
                elapsed = int(time.perf_counter() - start)
                counter += count

                chunk_rates.append(rate)
                avg_chunk_rate = int(sum(chunk_rates)/samples)


                perfect = avg_chunk_rate * max_workers
                actual = int(counter / elapsed)
                actual_rates.append(actual)
                avg_actual_rate = int(sum(actual_rates)/samples)

                overhead = int(100 - ((actual / perfect) * 100))
                overheads.append(overhead)
                avg_overhead = int(sum(overheads)/samples)

                report_progress(counter, avg_chunk_rate, avg_actual_rate, avg_overhead)
        end = time.perf_counter()
        complete = time.perf_counter()
        print('master scheduling time:%s complete_time:%s b/s: %s' % (
         end - start, complete - start, 1 / ((complete - start) / chunk_size)
        ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="populate s3 storage")
    parser.add_argument('filename', type=str)
    parser.add_argument('--max_workers', type=int, default=10)
    parser.add_argument('--max_threads', type=int, default=20)
    parser.add_argument('--chunk_size', type=int, default=1000)
    args = parser.parse_args()
    filename = args.filename
    max_workers = args.max_workers
    max_threads = args.max_threads
    chunk_size = args.chunk_size
    populate(filename, max_workers, max_threads, chunk_size)
