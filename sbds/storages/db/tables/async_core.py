# -*- coding: utf-8 -*-

import asyncio
import concurrent.futures
from copy import deepcopy
from functools import singledispatch
from itertools import chain


import dateutil.parser


import structlog
import uvloop

import sbds.sbds_json
from sbds.utils import block_num_from_previous

logger = structlog.get_logger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
LOOP = asyncio.get_event_loop()
EXECUTOR = concurrent.futures.ThreadPoolExecutor()

# pylint: disable=line-too-long
def from_raw_block(raw_block, session=None):
    """
    Extract and instantiate Block and Ops from raw block.

    Args:
        raw_block (Dict[str, str]):
        session (sqlalchemy.orm.session.Session):

    Returns:
        Tuple[Block, List[BaseOperation,None])
    """
    from sbds.storages.db.tables.block import Block
    from .operations.base import BaseOperation
    if session:
        block = Block.get_or_create_from_raw_block(raw_block, session=session)
    else:
        block = Block.from_raw_block(raw_block)
    tx_transactions = BaseOperation.from_raw_block(raw_block)
    return block, tx_transactions


async def prepare_raw_block(raw_block):
    """
        Convert raw block to dict, adding block_num.

        Args:
            raw_block (Union[Dict[str, List], Dict[str, str]]):

        Returns:
            Union[Dict[str, List], None]:
    """
    if isinstance(raw_block, dict):
        block_dict = await load_raw_block_from_dict(raw_block)
    elif isinstance(raw_block, str):
        block_dict = await load_raw_block_from_str(raw_block)
    elif isinstance(raw_block, bytes):
        block_dict = await load_raw_block_from_bytes(raw_block)
    else:
        raise TypeError(f'Unsupported raw_block type: {type(raw_block)}')
    




async def load_raw_block_from_dict(raw_block):
    block_dict = dict()
    block_dict.update(raw_block)
    block_dict['raw'] = sbds.sbds_json.dumps(block_dict, ensure_ascii=True)
    if 'block_num' not in block_dict:
        block_num = block_num_from_previous(block_dict['previous'])
        block_dict['block_num'] = block_num
    if isinstance(block_dict.get('timestamp'), str):
        timestamp = dateutil.parser.parse(block_dict['timestamp'])
        block_dict['timestamp'] = timestamp
    return block_dict



async def load_raw_block_from_str(raw_block):
    block_dict = dict()
    block_dict.update(sbds.sbds_json.loads(raw_block))
    block_dict['raw'] = raw_block
    return block_dict


async def load_raw_block_from_bytes(raw_block):
    block_dict = dict()
    block_dict['raw'] = raw_block.decode('utf8')
    block_dict.update(**sbds.sbds_json.loads(block_dict['raw']))
    return block_dict


async def get_block_num(block_dict):
    block_num = block_dict.get('block_num')
    if not block_num:
        return block_num_from_previous(block_dict['previous'])
    return block_num

async def get_parsed_timestamp(block_dict):
    timestamp = block_dict.get('timestamp')
    if isinstance(timestamp, str):
        return LOOP.run_in_executor(EXECUTOR, dateutil.parser.parse,timestamp)
    return timestamp


async def extract_transactions_from_blocks(blocks):
    """

    Args:
        blocks ():

    Returns:

    """
    transactions = chain.from_iterable(
        map(extract_transactions_from_block, blocks))
    return transactions


def extract_transactions_from_block(_block):
    """

    Args:
        _block (Dict[str, str]):

    Returns:

    """
    block = prepare_raw_block(_block)
    block_transactions = deepcopy(block['transactions'])
    for transaction_num, original_tx in enumerate(block_transactions, 1):
        tx = deepcopy(original_tx)
        yield dict(
            block_num=block['block_num'],
            timestamp=block['timestamp'],
            transaction_num=transaction_num,
            ref_block_num=tx['ref_block_num'],
            ref_block_prefix=tx['ref_block_prefix'],
            expiration=tx['expiration'],
            type=tx['operations'][0][0],
            operations=tx['operations'])


def extract_operations_from_block(raw_block):
    """

    Args:
        raw_block (Dict[str, str]):

    Returns:
    """
    block = prepare_raw_block(raw_block)
    transactions = extract_transactions_from_block(block)
    for transaction in transactions:
        for op_num, _operation in enumerate(transaction['operations'], 1):
            operation = deepcopy(_operation)
            op_type, op = operation
            op.update(
                block_num=transaction['block_num'],
                transaction_num=transaction['transaction_num'],
                operation_num=op_num,
                timestamp=block['timestamp'],
                type=op_type)
            yield op


def extract_operations_from_blocks(blocks):
    """

    Args:
        blocks ():

    Returns:

    """
    operations = chain.from_iterable(
        map(extract_operations_from_block, blocks))
    return operations
