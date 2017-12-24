# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Numeric, Integer, Enum
from toolz import get_in

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class WitnessUpdateOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 1306647607,
        "expiration": "2016-04-26T02:53:27",
        "operations": [
            [
                "witness_update",
                {
                    "owner": "arhag",
                    "block_signing_key": "STM5VNk9doxq55YEuyFw6qpNQt7q8neBWHhrau52fjV8N3TjNNUMP",
                    "props": {
                        "account_creation_fee": "100.000 STEEM",
                        "sbd_interest_rate": 1000,
                        "maximum_block_size": 131072
                    },
                    "url": " ",
                    "fee": "0.000 STEEM"
                }
            ]
        ],
        "signatures": [
            "1f2183af215f6878a080b659c4a302ce2c67f0df4c9914872d90cf129e6d1793b11401715e130af0da60f5a5a95c48b8de30140dd9884cbc812a017aab5c2b8b5c"
        ],
        "ref_block_num": 64732,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_witness_updates'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    owner = Column(Unicode(50), nullable=False)
    url = Column(Unicode(250), nullable=False)
    block_signing_key = Column(Unicode(64), nullable=False)
    props_account_creation_fee = Column(Numeric(15, 6), nullable=False)
    props_maximum_block_size = Column(Integer, nullable=False)
    props_sbd_interest_rate = Column(Integer, nullable=False)
    fee = Column(Numeric(15, 6), nullable=False, default=0.0)

    _fields = dict(
        owner=lambda x: x.get('owner'),
        url=lambda x: x.get('url'),
        block_signing_key=lambda x: x.get('block_signing_key'),
        props_account_creation_fee=lambda x: amount_field(
            x.get('account_creation_fee'), num_func=float, no_value=0),
        props_maximum_block_size=lambda x: get_in(
            ['props', 'maximum_block_size'], x),
        props_sbd_interest_rate=lambda x: get_in(
            ['props', 'sbd_interest_rate'], x),
        fee=lambda x: amount_field(x.get('fee'), num_func=float)
    )


    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)




