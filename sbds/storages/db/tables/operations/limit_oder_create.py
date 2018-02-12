# coding=utf-8

import os.path

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Numeric
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from .base import BaseOperation


class LimitOrderCreateOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 843461126,
        "expiration": "2016-07-01T13:33:03",
        "operations": [
            [
                "limit_order_create",
                {
                    "owner": "adm",
                    "amount_to_sell": "5.000 STEEM",
                    "min_to_receive": "1.542 SBD",
                    "orderid": 9,
                    "fill_or_kill": false,
                    "expiration": "2016-07-01T13:34:03"
                }
            ]
        ],
        "signatures": [
            "1f28e4e49e31cb9f22176fe142b3334d2459ec75cd70e48b2f536f6dc38deb8e8e5402e2cb878e0bc8cee2dc1280c480acdabe5807de5f7bc5c59ccf788920cdeb"
        ],
        "ref_block_num": 969,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_limit_order_creates'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    owner = Column(Unicode(50), nullable=False)
    orderid = Column(BigInteger, nullable=False)
    cancel = Column(Boolean, default=False)
    amount_to_sell = Column(Numeric(15, 6))
    # sell_symbol = Column(Unicode(5))
    min_to_receive = Column(Numeric(15, 6))
    # receive_symbol = Column(Unicode(5))
    fill_or_kill = Column(Boolean, default=False)
    expiration = Column(DateTime)

    _fields = dict(
        owner=lambda x: x.get('owner'),
        orderid=lambda x: x.get('orderid'),
        cancel=lambda x: x.get('cancel'),
        amount_to_sell=lambda x: amount_field(x.get('amount_to_sell'), num_func=float),
        # sell_symbol=lambda x: x['amount_to_sell'].split()[1],
        min_to_receive=lambda x: amount_field(x.get('min_to_receive'), num_func=float),
        # receive_symbol=lambda x: x['min_to_receive'].split()[1],
        fill_or_kill=lambda x: x.get('fill_or_kill'),
        expiration=lambda x: x.get('expiration'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
