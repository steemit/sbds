# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Numeric, Integer, Enum

from ...field_handlers import amount_field, amount_symbol_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class TransferFromSavingsOperation(Base, BaseOperation):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 57927444,
        "expiration": "2016-10-11T17:23:06",
        "operations": [
            [
                "transfer_from_savings",
                {
                    "amount": "0.051 STEEM",
                    "to": "knozaki2015",
                    "request_id": 1476206568,
                    "memo": "",
                    "from": "knozaki2015"
                }
            ]
        ],
        "signatures": [
            "205230e01b4def2d4e5a7d0446dd8c41874689155e5c739fc9a6a7d339303a5f135aa89cad21b568ef9f68d15bfaaf85e9fcc78bd544d9831c977a9b1ac578f726"
        ],
        "ref_block_num": 42559,
        "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_transfer_from_savings'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    _from = Column('from', Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    amount = Column(Numeric(15, 6))
    amount_symbol = Column(Unicode(5))
    memo = Column(Unicode(2048))
    request_id = Column(Integer)

    _fields = dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x['amount']),
        memo=lambda x: x.get('memo'),
        request_id=lambda x: x.get('request_id')
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

