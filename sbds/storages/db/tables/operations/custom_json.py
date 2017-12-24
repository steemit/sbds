# coding=utf-8

import os.path


import os.path
from sqlalchemy import Column, Unicode, UnicodeText, Enum

import sbds.sbds_json
from ...field_handlers import json_string_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class CustomJSONOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 1629956753,
        "ref_block_num": 10739,
        "operations": [
            [
                "custom_json",
                {
                    "id": "follow",
                    "json": "[\"follow\",{\"follower\":\"joanaltres\",\"following\":\"str8jackitjake\",\"what\":[\"blog\"]}]",
                    "required_posting_auths": [
                        "joanaltres"
                    ],
                    "required_auths": []
                }
            ]
        ],
        "expiration": "2017-02-26T15:54:57",
        "signatures": [
            "200d43fadd4a11d02d2dca36d0092b4439b674db406c024d9ef0eef08041a9500b45e5807a69d9e8ed9457ee675ba76ccdaee1587bef9902a680da7fd7f498e620"
        ],
        "extensions": []
    }
    """

    __tablename__ = 'sbds_op_custom_jsons'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    tid = Column(Unicode(50), nullable=False, index=True)
    required_auths = Column(Unicode(250))
    required_posting_auths = Column(Unicode(250))
    json = Column(UnicodeText)

    _fields = dict(
        tid=lambda x: x.get('id'),
        json=lambda x: x.get('json'),
        required_auths=lambda x: json_string_field(x.get('required_auths')),
        required_posting_auths=lambda x: json_string_field(x.get('required_posting_auths')), )


    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)



    def to_dict(self, decode_json=True):
        data_dict = self.dump()
        if isinstance(data_dict.get('required_auths'), str) and decode_json:
            data_dict['required_auths'] = sbds.sbds_json.loads(
                data_dict['required_auths'])
        if isinstance(data_dict.get('required_posting_auths'),
                      str) and decode_json:
            data_dict['required_posting_auths'] = sbds.sbds_json.loads(
                data_dict['required_posting_auths'])
        if isinstance(data_dict.get('json'), str) and decode_json:
            data_dict['json'] = sbds.sbds_json.loads(data_dict['json'])
        return data_dict