# -*- coding: utf-8 -*-
import datetime
import json
import math
import os
from collections import defaultdict
from urllib.parse import urlparse

import w3lib.url

import sbds.logging

logger = sbds.logging.getLogger(__name__)


# first 4 bytes (8 hex digits) of the block ID represents the block number
def block_num_from_hash(block_hash: str) -> int:
    return int(str(block_hash)[:8], base=16)


def block_num_from_previous(previous_block_hash: str) -> int:
    return block_num_from_hash(previous_block_hash) + 1


def percentile(n, percent, key=lambda x: x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not n:
        return None
    k = (len(n) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(n[int(k)])
    d0 = key(n[int(f)]) * (c - k)
    d1 = key(n[int(c)]) * (k - f)
    return d0 + d1


def chunkify(iterable, chunksize=10000):
    """Yield successive chunksized chunks from iterable."""
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


def write_json_items(items, filename=None, topic='', ext='json'):
    filename = filename or timestamp_filename(topic=topic, ext=ext)
    try:
        lineitems = os.linesep.join(
                json.dumps(item, ensure_ascii=True) for item in items)
        with open(filename, mode='a', encoding='utf8') as f:
            f.writelines(lineitems)
    except Exception as e:
        logger.error(e)


def write_json(items, dirname=None, prefix='sbds_error_', topic='', ext='json'):
    filename = timestamp_filename(topic=topic, prefix=prefix, ext=ext)
    dirname = dirname or 'failed_blocks'
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    path = os.path.join(dirname, filename)
    try:
        with open(path, mode='at', encoding='utf8', errors='replace') as f:
            json.dump(items, f, ensure_ascii=True)
        return True
    except Exception as e:
        logger.exception(e)
        logger.error(items)
        return False


def timestamp_filename(topic='', prefix=None, ext='json'):
    prefix = prefix or ''
    while True:
        now = datetime.datetime.now().isoformat().replace(':', '-').replace('.',
                                                                            '-')
        filename = '{prefix}{now}_{topic}.{ext}'.format(prefix=prefix, now=now,
                                                        topic=topic, ext=ext)
        if not os.path.exists(filename):
            break
    return filename


def json_metadata_keys(operations):
    jm_keys = defaultdict(set)
    for op in operations:
        if 'json_metadata' in op and op['json_metadata']:
            jm = jm2 = None
            try:
                jm = json.loads(op['json_metadata'])
                if isinstance(jm, dict):
                    jm_keys[op['type']].update(jm.keys())
                elif isinstance(jm, str):
                    jm2 = json.loads(jm)
                    jm_keys[op['type']].update(jm2.keys())
                else:
                    print('op_type:%s type:%s jm:%s jm2:%s orig:%s' % (
                        op['type'], type(jm), jm, jm2, op['json_metadata']))
            except Exception as e:
                print('op_type:%s orig:%s jm:%s jm2:%s error:%s' % (
                    op['type'], op['json_metadata'], jm, jm2, e))
    return jm_keys


def block_info(block):
    from sbds.storages.db.tables.core import prepare_raw_block
    block_dict = prepare_raw_block(block)
    info = dict(block_num=block_dict['block_num'],
                transaction_count=len(block_dict['transactions']),
                operation_count=sum(len(t['operations']) for t in
                                    block_dict['transactions']),
                transactions=[],
                )
    info[
        'brief'] = 'block: {block_num} transaction_types: {transactions} total_operations: {operation_count}'

    for t in block_dict['transactions']:
        info['transactions'].append(t['operations'][0][0])
    return info


def build_comment_url(parent_permlink=None, author=None, permlink=None):
    return '/'.join([parent_permlink, author, permlink])


def canonicalize_url(url, **kwargs):
    try:
        canonical_url = w3lib.url.canonicalize_url(url, **kwargs)
    except Exception as e:
        logger.warn('url preparation error', extra=dict(url=url, error=e))
        raise e
    if canonical_url != url:
        _log = dict(url=url, canonical_url=canonical_url)
        logger.info('canonical_url not equal to url', extra=_log)
    parsed_url = urlparse(canonical_url)
    if not parsed_url.scheme and not parsed_url.netloc:
        _log = dict(url=url, canonical_url=canonical_url, parsed_url=parsed_url)
        logger.warn('bad url encountered', extra=_log)
        return None
    return canonical_url
