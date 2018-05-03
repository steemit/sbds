# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse

import w3lib.url

import structlog

logger = structlog.get_logger(__name__)


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


def chunkify(iterable, chunksize=10000):
    """Yield successive chunksized chunks from iterable.

    Args:
      iterable:
      chunksize:  (Default value = 10000)

    Returns:

    """
    i = 0
    chunk = []
    for item in iterable:
        chunk.append(item)
        i += 1
        if i == chunksize:
            yield chunk
            i = 0
            chunk = []
    if chunk:
        yield chunk


def build_comment_url(parent_permlink=None, author=None, permlink=None):
    return '/'.join([parent_permlink, author, permlink])


def canonicalize_url(url, **kwargs):
    try:
        canonical_url = w3lib.url.canonicalize_url(url, **kwargs)
    except Exception as e:
        logger.warning('url preparation error', extra=dict(url=url, error=e))
        return None
    if canonical_url != url:
        logger.debug('canonical_url changed %s to %s', url, canonical_url)
    try:
        parsed_url = urlparse(canonical_url)
        if not parsed_url.scheme and not parsed_url.netloc:
            _log = dict(
                url=url, canonical_url=canonical_url, parsed_url=parsed_url)
            logger.warning('bad url encountered', extra=_log)
            return None
    except Exception as e:
        logger.warning('url parse error', extra=dict(url=url, error=e))
        return None
    return canonical_url
