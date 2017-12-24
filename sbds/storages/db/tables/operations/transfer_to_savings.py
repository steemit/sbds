# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Numeric, Enum

from ...field_handlers import amount_field, amount_symbol_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class TransferToSavingsOperation(Base, BaseOperation):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 2803959602,
        "expiration": "2016-10-10T16:41:45",
        "operations": [
            [
                "transfer_to_savings",
                {
                    "amount": "1000.000 SBD",
                    "to": "jamesc",
                    "memo": "",
                    "from": "jamesc"
                }
            ]
        ],
        "signatures": [
            "1f248e64af20e24ad88078b101dba8d565aa1a6bde7ce105bed11a261f5aea9d4b6aca52f3aae23f8b98526ebeede8974407a972a85606036c304020cb2af28afb"
        ],
        "ref_block_num": 12870,
        "extensions": []
    }




    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_transfer_to_savings'
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

