# coding=utf-8

import os.path


import os.path
from sqlalchemy import Column, Unicode, UnicodeText, Enum

import sbds.sbds_json
from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class CustomOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 449600556,
        "ref_block_num": 54561,
        "operations": [
            [
                "custom",
                {
                    "id": 777,
                    "data": "066e6f69737932056c656e6b61032e0640ec51dbcfb761bd927a732e134deff42dbed04bc42300f27f3048b8b44802be956c36eef2e0d3594b794b428a21b48fe41874d41cf12feb8e421e11b3702f24e94b559f4505006dbafb90208bf88f7bb550f6db0713cbb4be6c214c50c16aa62413383f26f9efbb4fe5bf3f",
                    "required_auths": [
                        "noisy2"
                    ]
                }
            ]
        ],
        "expiration": "2017-01-09T01:32:36",
        "signatures": [
            "1f38daabe10814c20f78bba5cbeed5f9115eb9d420278540bddf9e3c6e84fe3ca33da6b32127faf0d30cc0d618711edd294b95fa92787398cb7f0dfb7280509db3"
        ],
        "extensions": []
    }
    """

    __tablename__ = 'sbds_op_customs'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    tid = Column(Unicode(50), nullable=False)
    required_auths = Column(Unicode(250))
    data = Column(UnicodeText)

    _fields = dict(
        tid=lambda x: x.get('id'),
        data=lambda x: x.get('data'),
        required_auths=lambda x: x.get('required_auths'), )


    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)



    def to_dict(self, decode_json=True):
        data_dict = self.dump()
        if isinstance(data_dict.get('required_auths'), str) and decode_json:
            data_dict['required_auths'] = sbds.sbds_json.loads(
                data_dict['required_auths'])
        return data_dict