# -*- coding: utf-8 -*-
import math

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