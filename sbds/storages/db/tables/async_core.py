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
from sbds.storages.db.tables.operations import op_class_for_type

logger = structlog.get_logger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
LOOP = asyncio.get_event_loop()
EXECUTOR = concurrent.futures.ThreadPoolExecutor()


async def prepare_raw_block_for_storage(raw_block, loop=None):
    block_dict = await load_raw_block(raw_block, loop=loop)
    return dict(
            raw=block_dict['raw'],
            block_num=block_dict['block_num'],
            previous=block_dict['previous'],
            timestamp=block_dict['timestamp'],
            witness=block_dict['witness'],
            witness_signature=block_dict['witness_signature'],
            transaction_merkle_root=block_dict['transaction_merkle_root'])

async def load_raw_block(raw_block, loop=None):
    """
        Convert raw block to dict, add block_num and parse timestamp into datetime

        This is the async version which inlines functions from `sbds.storages.db.core`
        for speedup during initial syncing

        Args:
            raw_block (Union[Dict[str, Any], str, bytes]):

        Returns:
            Dict[str, List]:
    """

    if isinstance(raw_block, dict):
        block_dict = dict()
        block_dict.update(raw_block)
        block_dict['raw'] = await loop.run_in_executor(EXECUTOR, sbds.sbds_json.dumps,block_dict)
    elif isinstance(raw_block, str):
        block_dict = await loop.run_in_executor(EXECUTOR, sbds.sbds_json.loads, raw_block)
        block_dict['raw'] = raw_block
    elif isinstance(raw_block, bytes):
        block_dict = await loop.run_in_executor(EXECUTOR, sbds.sbds_json.loads,
                                                raw_block)
        block_dict['raw'] = raw_block.decode('utf8')
    else:
        raise TypeError(f'Unsupported raw_block type: {type(raw_block)}')

    if not block_dict.get('block_num'):
        block_dict['block_num'] = block_num_from_previous(block_dict['previous'])
    timestamp = block_dict.get('timestamp')
    if isinstance(timestamp, str):
        block_dict['timestamp']  = await loop.run_in_executor(EXECUTOR, dateutil.parser.parse, timestamp)

    return block_dict


async def load_raw_operation(raw_operation, loop=None):
    """Load operation fronm response of get_ops_in_block calls

    {
        "block": 14000000,
        "op": [
            "vote",
            {
                "author": "ihhira",
                "permlink": "upvote-and-comment-3",
                "voter": "ihhira",
                "weight": 10000
            }
        ],
        "op_in_trx": 0,
        "timestamp": "2017-07-25T18:58:12",
        "trx_id": "b683651bb9cee85fef0a2150cb6d81ee090f5b74",
        "trx_in_block": 40,
        "virtual_op": 0
    }



    """
    raw_operation['timestamp'] = await loop.run_in_executor(EXECUTOR, dateutil.parser.parse, raw_operation['timestamp'])
    return {
        'block_num': raw_operation['block'],
        'transaction_num': raw_operation['trx_in_block'],
        'operation_num': raw_operation['op_in_trx'],
        'timestamp': raw_operation['timestamp'],
        'trx_id': raw_operation['trx_id'],
        'op_type': raw_operation['op'][0][0],
        'virtual_op': raw_operation['virtual_op'],
        'data': raw_operation['op'][0][1]
    }

async def prepare_opertaion_for_storage(op_dict, loop=None):
    op_cls = op_class_for_type(op_dict['type'])
    _fields = op_cls._fields
    prepared_fields = await loop.run_in_executor(EXECUTOR, prepare_op_class_fields, op_dict['data'], _fields)
    op_dict.update(prepared_fields)
    del op_dict['data']
    return op_dict

def prepare_op_class_fields(op_dict_data, fields):
    return {k: v(op_dict_data) for k, v in fields.items()}
