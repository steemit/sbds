# -*- coding: utf-8 -*-


from copy import deepcopy
from functools import singledispatch
from itertools import chain

import maya

import sbds.sbds_json
import structlog
from sbds.storages.db.tables.block import Block
from sbds.utils import block_num_from_previous

logger = structlog.get_logger(__name__)

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

    from .operations.base import BaseOperation
    if session:
        block = Block.get_or_create_from_raw_block(raw_block, session=session)
    else:
        block = Block.from_raw_block(raw_block)
    tx_transactions = BaseOperation.from_raw_block(raw_block)
    return block, tx_transactions


def prepare_raw_block(raw_block):
    """
        Convert raw block to dict, adding block_num.

        Args:
            raw_block (Union[Dict[str, List], Dict[str, str]]):

        Returns:
            Union[Dict[str, List], None]:
    """
    block_dict = load_raw_block(raw_block)
    block_dict = add_block_num(block_dict)
    block_dict = parse_timestamp(block_dict)
    return block_dict


@singledispatch
def load_raw_block(raw_block):
    raise TypeError(f'Unsupported raw block type: {type(raw_block)}')


# noinspection PyUnresolvedReferences
@load_raw_block.register(dict)
def load_raw_block_from_dict(raw_block):
    block_dict = dict()
    block = deepcopy(raw_block)
    block_dict.update(**block)
    block_dict['raw'] = sbds.sbds_json.dumps(block, ensure_ascii=True)
    return block_dict


# noinspection PyUnresolvedReferences
@load_raw_block.register(str)
def load_raw_block_from_str(raw_block):
    block_dict = dict()
    block_dict.update(**sbds.sbds_json.loads(raw_block))
    block_dict['raw'] = raw_block


# noinspection PyUnresolvedReferences
@load_raw_block.register(bytes)
def load_raw_block_from_bytes(raw_block):
    block_dict = dict()
    block_dict['raw'] = raw_block.decode('utf8')
    block_dict.update(**sbds.sbds_json.loads(block_dict['raw']))
    return block_dict


def add_block_num(block_dict):
    if 'block_num' not in block_dict:
        block_num = block_num_from_previous(block_dict['previous'])
        block_dict['block_num'] = block_num
    return block_dict

def parse_timestamp(block_dict):
    if isinstance(block_dict.get('timestamp'), str):
        timestamp = maya.dateparser.parse(block_dict['timestamp'])
        block_dict['timestamp'] = timestamp
    return block_dict


def extract_transactions_from_blocks(blocks):
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
