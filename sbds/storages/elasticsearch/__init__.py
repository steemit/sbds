# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from collections import defaultdict

from elasticsearch_dsl import DocType, Date, Nested,  \
    analyzer, InnerObjectWrapper, Integer, String, Object
from elasticsearch_dsl import MetaField


from sbds.utils import block_num_from_previous



class Operation(DocType):
    # block
    block = Object(properties=dict(
            witness=String(fields={'raw': String(index='not_analyzed')}),
            transaction_merkle_root=String(),
            extensions=String(multi=True),
            witness_signature=String()
    ))

    # transaction
    transaction = Object(
        properties=dict(
                block_num=Integer(),
                previous = String(),
                timestamp = Date(),
                witness = String(fields={'raw': String(index='not_analyzed')}),
                transaction_merkle_root = String(),
                extensions = String(multi=True),
                witness_signature = String(),
        )
    )


    operation_num = Integer()
    op_type = String(index='not_analyzed')
    block_id = String()
    work = Object()
    nonce = String()
    props = Object()
    worker_account = String()


    class Meta:
        index = 'blocks'
        type = 'operation'



def prepare_block(orig_block):
    block = deepcopy(orig_block)

    if not isinstance(block, dict):

        block_dict = json.loads(block)
    else:
        block_dict = block

    # block_num
    block_num = int(block_num_from_previous(block_dict['previous']))
    block_dict.update(block_num=block_num)

    operation_dict = dict()

    operation_dict['timestamp'] = block_dict['timestamp']
    operation_dict['_id'] = str(block_num)
    operation_dict['block'] = deepcopy(block_dict)


    if 'transactions' in operation_dict['block']:
        del operation_dict['block']['transactions']

    if len(block_dict['transactions']) == 0:
        yield operation_dict

    # transactions
    for transaction_num, raw_trans in enumerate(block_dict.get('transactions')):
        trans_dict = deepcopy(raw_trans)
        trans_dict['transaction_num']=transaction_num
        operation_dict['transaction'] = deepcopy(trans_dict)


        # operations
        for operation_num ,raw_op in enumerate(trans_dict.get('operations')):
            tmp_operation_dict = deepcopy(operation_dict)
            op_type, raw_op_dict = raw_op
            tmp_operation_dict.update(**raw_op_dict)
            tmp_operation_dict['op_type'] = op_type
            tmp_operation_dict['_id'] = '%s/%s/%s' % (block_num,transaction_num,operation_num)
            if 'operations' in tmp_operation_dict['transaction']:
                del tmp_operation_dict['transaction']['operations']
            yield tmp_operation_dict



def init_all(es):
    es.indices.delete('blocks')
    es.indices.create('blocks')
    Operation.init()


def all_from_block(raw_block):
        operations = prepare_block(raw_block)
        results = []
        for operation_dict in operations:
            operation = Operation(**operation_dict)
            operation.save()


def prepare_bulk_block(block, _index='blocks', _op_type='index'):
    operations = prepare_block(block)
    for operation_dict in operations:
        yield dict(_source=operation_dict,
                    _index=_index,
                    _op_type=_op_type,
                   _type='operation')
