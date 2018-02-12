# -*- coding: utf-8 -*-

from copy import copy
from copy import deepcopy
from itertools import chain

import maya

import sbds.sbds_json
import sbds.sbds_logging
from sbds.storages.db.tables.block import Block
from sbds.utils import block_num_from_previous

logger = sbds.sbds_logging.getLogger(__name__)

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
    block_dict = dict()
    if isinstance(raw_block, dict):
        block = deepcopy(raw_block)
        block_dict.update(**block)
        block_dict['raw'] = sbds.sbds_json.dumps(block, ensure_ascii=True)
    elif isinstance(raw_block, str):
        block_dict.update(**sbds.sbds_json.loads(raw_block))
        block_dict['raw'] = copy(raw_block)
    elif isinstance(raw_block, bytes):
        block = deepcopy(raw_block)
        raw = block.decode('utf8')
        block_dict.update(**sbds.sbds_json.loads(raw))
        block_dict['raw'] = copy(raw)
    else:
        raise TypeError('Unsupported raw block type')
    if 'block_num' not in block_dict:
        block_num = block_num_from_previous(block_dict['previous'])
        block_dict['block_num'] = block_num
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
