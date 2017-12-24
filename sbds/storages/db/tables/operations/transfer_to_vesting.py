# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Numeric, Enum

from ...field_handlers import amount_field,amount_symbol_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class TransferToVestingOperation(Base, BaseOperation):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 4131173691,
        "expiration": "2016-03-27T06:55:27",
        "operations": [
            [
                "transfer_to_vesting",
                {
                    "amount": "20.000 STEEM",
                    "to": "itsascam",
                    "from": "james"
                }
            ]
        ],
        "signatures": [
            "1f2853e69b7cf718f53e97c637a348115e17ae3995c773c28445c46b12ccf3716664aca8e82963f343a061ce0e097c29fa3e07ee9dc61d372bb14882b3106547a0"
        ],
        "ref_block_num": 9132,
        "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_transfer_to_vestings'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    _from = Column('from', Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    amount = Column(Numeric(15, 6))
    amount_symbol = Column(Unicode(5))

    _fields = dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x['amount'])
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

