# -*- coding: utf-8 -*-

import json
from copy import deepcopy
from elasticsearch_dsl import DocType, Date, Nested,  \
    analyzer, InnerObjectWrapper, Integer, String
from sbds.utils import block_num_from_previous


class Operation(InnerObjectWrapper):
    # op_type = String()
    pass

class Transaction(InnerObjectWrapper):
    '''
    expiration = Date()
    extensions = String(multi=True)
    signatures = String(multi=True)

    ref_block_num = Integer()
    ref_block_prefix = String()
    operations = Nested(doc_class=Operation)
    '''
    pass

class Block(DocType):
    block_num = Integer()
    previous = String()
    timestamp = Date()
    witness = String(fields={'raw': String(index='not_analyzed')})
    transaction_merkle_root = String()
    extensions = String(multi=True)
    witness_signature = String()
    transactions = Nested(doc_class=Transaction,
                  properties=dict(
                          expiration=Date(),
                            extensions=String(multi=True),
                            signatures=String(multi=True),
                            ref_block_num=Integer(),
                            ref_block_prefix=String(fields={'raw': String(index='not_analyzed')}),
                            operations=Nested(doc_class=Operation, properties=dict(
                                op_type=String(fields={'raw': String(index='not_analyzed')})
                                )
                            )
                        )
                  )

    class Meta:
        index = 'blocks'

    @classmethod
    def from_block(cls, block, *args, **kwargs):
        prepared_block = prepare_block(block)
        kwargs.update(**prepared_block)
        return cls(*args, **kwargs)

    def save(self, ** kwargs):
        self.meta.id = self.block_num
        return super().save(** kwargs)

def prepare_block(orig_block):
    block = deepcopy(orig_block)

    if not isinstance(block, dict):

        block_dict = json.loads(block)
    else:
        block_dict = block

    # block_num
    block_num = block_num_from_previous(block_dict['previous'])
    block_dict.update(block_num=block_num)

    # transactions
    transactions = []

    for transaction_num, raw_trans in enumerate(block_dict.get('transactions')):
        raw_trans.update(block_num=block_num)
        raw_trans.update(transaction_num=transaction_num)

        # operations
        operations = []
        for raw_op in raw_trans.get('operations'):
            op_type, operation = raw_op
            operation['op_type'] = op_type
            operations.append(operation)
        raw_trans['operations'] = operations
        transactions.append(raw_trans)
    block_dict['transactions'] = transactions
    return block_dict

def prepare_bulk_block(block, _index='blocks', _type='block', _op_type='index'):
    bulk_block = prepare_block(block)
    bulk_block['_id']=bulk_block['block_num']
    return dict(**bulk_block, _index=_index, _type=_type, _op_type=_op_type)
