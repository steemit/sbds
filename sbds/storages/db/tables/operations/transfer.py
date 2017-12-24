# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Numeric, Enum

from ...field_handlers import amount_field, amount_symbol_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class TransferOperation(Base, BaseOperation):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 4211555470,
        "expiration": "2016-03-25T13:49:33",
        "operations": [
            [
                "transfer",
                {
                    "amount": "833.000 STEEM",
                    "to": "steemit",
                    "memo": "",
                    "from": "admin"
                }
            ]
        ],
        "signatures": [
            "204ffd40d4feefdf309780a62058e7944b6833595c500603f3bb66ddbbca2ea661391196a97aa7dde53fdcca8aeb31f8c63aee4f47a20238f3749d9f4cb77f03f5"
        ],
        "ref_block_num": 25501,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_transfers'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    _from = Column('from', Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    amount = Column(Numeric(15, 6))
    amount_symbol = Column(Unicode(5))
    memo = Column(Unicode(2048))

    _fields = dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x['amount']),
        memo=lambda x: x.get('memo')
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

