# -*- coding: utf-8 -*-

import json
from copy import deepcopy

from elasticsearch_dsl import DocType, Date, Float, Long, Mapping
from elasticsearch_dsl import Integer, String, Object, Nested

import sbds.logging
from sbds.storages import operation_types
from sbds.utils import block_num_from_previous
from sbds.utils import flatten_obj
from sbds.utils import safe_flatten_obj

logger = sbds.logging.getLogger(__name__)

op_type_objects = {op_type:Object() for op_type in operation_types}

class Operation(DocType):
    # block
    id = Long()
    block = Object(properties=dict(
            witness=String(fields={'raw': String(index='not_analyzed')}),
            transaction_merkle_root=String(),
            witness_signature=String(),
            raw=String()
    ))

    # transaction
    transaction = Object(
            properties=dict(
                    block_num=Integer(),
                    previous=String(),
                    timestamp=Date(),
                    witness=String(fields={'raw': String(index='not_analyzed')}),
                    transaction_merkle_root=String(),
                    extensions=String(multi=True),
                    witness_signature=String(),
            )
    )

    # operation
    operation = Object(properties=dict(
            operation_num=Integer(),
            op_type=String(index='not_analyzed')
    ))


    class Meta:
        index = 'blocks'
        doc_type = 'block_operation'

    dynamic_templates = [
        {
            "key_auths_long_as_strings": {
                "match_mapping_type": "long",
                "path_match": "operation.account*.*.*_auths",
                #"match": "key_auths",
                "mapping": {
                    "type": "string"
                }
            }
        },
        {
            "pow2": {
                "match_mapping_type": "long",
                "path_match": "operation.pow2.work",
                "mapping": {
                    "type": "object",
                    "fields":{
                        "raw": {"type":"string"}
                    }
                }
            }
        },
        {
            "extensions": {
                "match_mapping_type": "long",
                "path_match": "block.extensions",
                "mapping": {
                    "type": "string"
                }
            }
        }
    ]

    def save(self, *args, **kwargs):
        self.meta.id=self.id
        super(Operation, self).save(*args, **kwargs)

    @classmethod
    def init(cls, *args, **kwargs):
        super(Operation, cls).init(*args, **kwargs)
        m = cls._doc_type.mapping
        m.meta('dynamic_templates', cls.dynamic_templates)
        m.save('blocks')

def extract_operations_from_block(orig_block):
    base_doc_dict = dict()

    # block
    block = deepcopy(orig_block)
    if not isinstance(block, dict):
        block_dict = json.loads(block)
    else:
        block_dict = block

    block_num = block_num_from_previous(block_dict['previous'])
    block_dict['block_num'] = block_num
    #if len(block_dict['extensions']):
    #    block_dict['extensions'] = list(map(flatten_obj, block_dict['extensions']))
    base_doc_dict['block'] = deepcopy(block_dict)

    # return with just block if no transactions present
    if len(block_dict['transactions']) == 0:
        base_doc_dict['id'] = block_num
        if 'transactions' in base_doc_dict:
            del base_doc_dict['transactions']
        yield base_doc_dict

    # transactions
    for transaction_num, raw_trans in enumerate(block_dict['transactions']):
        trans_dict = deepcopy(raw_trans)
        trans_dict['transaction_num'] = transaction_num

        # operations
        for operation_num, raw_op in enumerate(trans_dict['operations']):
            op_type, raw_operation_dict = raw_op
            operation_dict = dict(op_type=op_type, operation_num=operation_num)
            if op_type in op_transforms:
                transformed = op_transforms[op_type](raw_operation_dict)
                operation_dict[op_type]=transformed
            else:
                operation_dict[op_type]=raw_operation_dict

            # final document dict
            doc_dict = deepcopy(base_doc_dict)
            _id = '%s%s%s' % (block_num, transaction_num, operation_num)
            doc_dict['id'] = int(_id)
            doc_dict['operation'] = operation_dict
            doc_dict['transaction'] = deepcopy(trans_dict)
            del doc_dict['block']['transactions']
            del doc_dict['transaction']['operations']
            yield doc_dict


def init_index(es, index='blocks'):
    try:
        es.indices.delete(index)
    except Exception as e:
        logger.info(e)
    try:
        es.indices.create(index)
        Operation(using=es).init()
    except Exception as e:
        logger.info(e)


def extract_from_block_and_save(raw_block):
    operations = extract_operations_from_block(raw_block)
    for operation_dict in operations:
        operation = Operation(**operation_dict)
        try:
            operation.save()
        except Exception as e:
            return e

def extract_bulk_operation_from_block(block, _index='blocks', _op_type='index'):
    operations = extract_operations_from_block(block)
    for operation_dict in operations:
        yield dict(_source=operation_dict,
                   _index=_index,
                   _op_type=_op_type,
                   _type='block_operation',
                   _id=int(operation_dict['id']))


def transform_pow2(op_dict):
    if not isinstance(op_dict['work'], list):
        op_dict['work'] = {}
    else:
        op_dict['work'] = op_dict['work'][1]
    return op_dict

def transform_key_auths(op_dict):
    for key in ('active','owner','posting'):
        for key2 in ('key_auths', 'account_auths'):
            try:
                op_dict[key][key2] = [str(i[0]) for i in op_dict[key][key2]]
            except:
                pass
    return op_dict



op_transforms = dict()
op_transforms['pow2'] = transform_pow2
#op_transforms['account_create'] = transform_key_auths
#op_transforms['account_update'] = transform_key_auths

