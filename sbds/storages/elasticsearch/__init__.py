# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from elasticsearch_dsl import DocType, Date, Nested,  \
    analyzer, InnerObjectWrapper, Integer, String, Object
from elasticsearch_dsl import MetaField


from sbds.utils import block_num_from_previous



class Operation(DocType):
    block_num = Integer()
    transaction_num = Integer()
    operation_num = Integer()
    op_type = String(index='not_analyzed')
    block_id = String()
    work = Object()
    nonce = String()
    props = Object()
    worker_account = String()

    # _id = blocknum/transaction_num/operation_num

    class Meta:
        index = 'blocks'
        type = 'operation'
        parent = MetaField(type='transaction')



class Transaction(DocType):
    block_num = Integer()
    transaction_num = Integer()
    expiration = Date()
    extensions = String(multi=True)
    signatures = String(multi=True)
    ref_block_num = Integer()
    ref_block_prefix = String()

    # _id = blocknum/transaction_num

    class Meta:
        index = 'blocks'
        type = 'transaction'
        parent = MetaField(type='block')





class Block(DocType):
    block_num = Integer()
    previous = String()
    timestamp = Date()
    witness = String(fields={'raw': String(index='not_analyzed')})
    transaction_merkle_root = String()
    extensions = String(multi=True)
    witness_signature = String()


    class Meta:
        index = 'blocks'
        type = 'block'

    @classmethod
    def from_block(cls, block, *args, **kwargs):
        prepared_block = prepare_block(block)
        es_block = cls()
        kwargs.update(**prepared_block)
        return cls(*args, **kwargs)

    def save(self, ** kwargs):
        return super().save(** kwargs)

def prepare_block(orig_block):
    block = deepcopy(orig_block)

    if not isinstance(block, dict):

        block_dict = json.loads(block)
    else:
        block_dict = block

    # block_num
    block_num = int(block_num_from_previous(block_dict['previous']))
    block_dict.update(block_num=block_num, _id=block_num)

    # transactions
    transactions = []
    operations = []
    for transaction_num, raw_trans in enumerate(block_dict.get('transactions')):
        trans_dict = deepcopy(raw_trans)
        trans_dict.update(block_num=block_num)
        trans_dict.update(transaction_num=transaction_num)
        trans_dict['timestamp'] = block_dict['timestamp']
        trans_dict['_id'] = '%s/%s' % (block_num, transaction_num)
        trans_dict['_parent'] = block_num

        # operations

        for operation_num ,raw_op in enumerate(trans_dict.get('operations')):
            op_type, operation_dict = deepcopy(raw_op)
            operation_dict['op_type'] = op_type
            operation_dict['transaction_num'] = transaction_num
            operation_dict['block_num'] = block_num
            operation_dict['_id'] = '%s/%s/%s' % (block_num,transaction_num,operation_num)
            operation_dict['_parent'] = trans_dict['_id']
            operation_dict['timestamp'] = block_dict['timestamp']
            #operation = Operation(**operation_dict)
            operations.append(operation_dict)
        if 'operations' in trans_dict:
            del trans_dict['operations']
        #transaction = Transaction(**trans_dict)
        transactions.append(trans_dict)
    if 'transactions' in block_dict:
        del block_dict['transactions']
    return block_dict, transactions, operations

def init_all(es):
    es.indices.delete('blocks')
    es.indices.create('blocks')
    Operation.init()
    Transaction().init()
    Block().init()




def all_from_block(raw_block):
        block_dict, transactions, operations = prepare_block(raw_block)
        block = Block(**block_dict)
        block.save()
        for trans_dict in transactions:
            transaction = Transaction(**trans_dict)
            transaction.save()
        for operation_dict in operations:
            operation = Operation(**operation_dict)
            operation.save()

def prepare_bulk_block(block, _index='blocks', _type='block', _op_type='index'):
    bulk_block = prepare_block(block)
    _id=int(bulk_block['block_num'])
    return dict(_source=bulk_block, _index=_index, _type=_type, _op_type=_op_type, _id=_id)
