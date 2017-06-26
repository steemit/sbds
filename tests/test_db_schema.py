# coding=utf-8

from sbds.storages.db.tables.tx import tx_class_map
from sbds.storages.db import tables

def all_operations_defined(operation_schema):
    op_name, schema = operation_schema
    assert op_name in tx_class_map

def test_operation_definition(operation_schema):
    name, schema = operation_schema
    schema_fields = schema['properties']
    if name not in tx_class_map:
        return
    cls = tx_class_map[name]
    cls_fields = cls._fields[name].keys()
    for schema_field_name, schema_val in schema_fields.items():
        adjusted_field_name = apply_schema_fieldname_adjustments(schema_field_name)
        assert adjusted_field_name in cls_fields


def apply_schema_fieldname_adjustments(field):
    field_map = {
        'from': '_from',
        #'owner': 'owner_key',
        #'memo': 'memo_key',
        'active': 'active_key',
        'posting': 'posting_key'
    }
    return field_map.get(field, field)