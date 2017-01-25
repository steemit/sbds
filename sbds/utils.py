# -*- coding: utf-8 -*-
import math
from itertools import chain
from collections import defaultdict
import json

import sbds.logging

logger = sbds.logging.getLogger(__name__)


# first 4 bytes (8 hex digits) of the block ID represents the block number
def block_num_from_hash(block_hash: str) -> int:
    return int(str(block_hash)[:8], base=16)


def block_num_from_previous(previous_block_hash: str) -> int:
    return block_num_from_hash(previous_block_hash) + 1


def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1


def chunkify(iterable, chunksize=10000):
    """Yield successive chunksized chunks from iterable."""
    i = 0
    chunk = []
    for item in iterable:
        chunk.append(item)
        i +=1
        if i == chunksize:
            yield chunk
            i = 0
            chunk = []
    if len(chunk) > 0:
        yield chunk

def flatten_obj(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + '[%s]' % i)
                i += 1
        else:

            out[name.rstrip('.')] =x

    flatten(y)
    return out



def build_op_type_maps(blocks):
    transactions = chain.from_iterable(b['transactions'] for b in blocks)
    operations = chain.from_iterable(t['operations'] for t in transactions)
    ops_dict=defaultdict(dict)
    for op_type, op in operations:
        keyval = {k:type(v) for k,v in op.items()}
        ops_dict[op_type][frozenset(keyval)]=flatten_obj(op)
    return ops_dict


def write_json_items(filename, items):
    try:
        lineitems = os.linesep.join(json.dumps(item, ensure_ascii=True) for item in items)
        with open(filename, mode='a', encoding='utf8') as f:
           f.writelines(lineitems)
    except Exception as e:
        logger.error(e)


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


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

def block_info(block_dict):
    info = dict(block_num=block_dict['block_num'],
                transaction_count=len(block_dict['transactions']),
                operation_count=sum(len(t['operations']) for t in block_dict['transactions']),
                transactions=[],
                )
    info['brief'] = 'block:{block_num} transaction_type:{transactions} total_operations:{operations_count}'

    for t in block_dict['transactions']:
        info['transactions'].append(t['operations'][0][0])
    return block_data

