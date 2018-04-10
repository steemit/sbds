# -*- coding: utf-8 -*-
import asyncio
import concurrent.futures

import ciso8601
import structlog
import uvloop

import sbds.sbds_json
from sbds.utils import block_num_from_previous
from sbds.storages.db.tables.operations import op_class_for_type
from sbds.storages.db.tables.meta.accounts import extract_account_names

logger = structlog.get_logger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
LOOP = asyncio.get_event_loop()
EXECUTOR = concurrent.futures.ThreadPoolExecutor()


async def async_extract_account_names(prepared_ops, loop=None, executor=EXECUTOR):
    return await loop.run_in_executor(executor, extract_account_names, prepared_ops)


async def prepare_raw_block_for_storage(raw_block, prepared_ops=None, loop=None, executor=EXECUTOR):
    block_dict = await load_raw_block(raw_block, loop=loop, executor=executor)
    accounts = await async_extract_account_names(prepared_ops, loop=loop, executor=executor)
    accounts.add(block_dict['witness'])

    return dict(
        raw=block_dict['raw'],
        block_num=block_dict['block_num'],
        previous=block_dict['previous'],
        timestamp=block_dict['timestamp'],
        witness=block_dict['witness'],
        witness_signature=block_dict['witness_signature'],
        transaction_merkle_root=block_dict['transaction_merkle_root'],
        accounts=sbds.sbds_json.dumps(list(accounts)),
        op_types=sbds.sbds_json.dumps(list(set(op['operation_type'] for op in prepared_ops)))
    )


async def load_raw_block(raw_block, loop=None, executor=EXECUTOR):
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
        block_dict['raw'] = await loop.run_in_executor(executor, sbds.sbds_json.dumps, block_dict)
    elif isinstance(raw_block, str):
        block_dict = await loop.run_in_executor(executor, sbds.sbds_json.loads, raw_block)
        block_dict['raw'] = raw_block
    elif isinstance(raw_block, bytes):
        block_dict = await loop.run_in_executor(executor, sbds.sbds_json.loads,
                                                raw_block)
        block_dict['raw'] = raw_block.decode('utf8')
    else:
        raise TypeError(f'Unsupported raw_block type: {type(raw_block)}')

    if not block_dict.get('block_num'):
        block_dict['block_num'] = block_num_from_previous(block_dict['previous'])
    timestamp = block_dict.get('timestamp')
    if isinstance(timestamp, str):
        block_dict['timestamp'] = ciso8601.parse_datetime(timestamp)

    return block_dict


async def prepare_raw_operation_for_storage(raw_operation, loop=None, executor=EXECUTOR):
    data = raw_operation['op'][1]
    op_dict = {
        'block_num': raw_operation['block'],
        'transaction_num': raw_operation['trx_in_block'],
        'operation_num': raw_operation['op_in_trx'],
        'timestamp': ciso8601.parse_datetime(raw_operation['timestamp']),
        'trx_id': raw_operation['trx_id'],
        'operation_type': raw_operation['op'][0],
        'raw': sbds.sbds_json.dumps(raw_operation['op'][1])
    }
    op_cls = op_class_for_type(op_dict['operation_type'])
    _fields = op_cls._fields
    prepared_fields = await loop.run_in_executor(executor, prepare_op_class_fields, data, _fields)
    op_dict.update(prepared_fields)
    op_dict.update({k: v for k, v in data.items() if k not in prepared_fields})
    return op_dict


def prepare_op_class_fields(op_dict_data, fields):
    return {k: v(op_dict_data) for k, v in fields.items()}
