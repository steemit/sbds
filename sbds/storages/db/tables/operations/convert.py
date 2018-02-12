# coding=utf-8

import os.path

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from .base import BaseOperation


class ConvertOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        'expiration': '2016-07-04T00:29:39',
        'extensions': [],
        'operations': [['convert',{
            'amount': '5.000 SBD',
            'owner': 'summon',
            'requestid': 1467592156
            }]],
        'ref_block_num': 5864,
        'ref_block_prefix': 521569582,
        'signatures': ['1f0cd39195d45d5d40cd92651081670b5a799217d615c311921fc1981a0898703d1864555148c2e1246a19fa8ea1b80b4dd4474df86fc9a9c9d6a9c8576d467687']
    }

    Prepared Format
    ===============
    {
        "owner": "summon",
        "amount": "5.000 SBD",
        "requestid": 1467592156
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_converts'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    owner = Column(Unicode(50), nullable=False)
    requestid = Column(BigInteger, nullable=False)
    amount = Column(Numeric(15, 6), nullable=False)

    _fields = dict(
        owner=lambda x: x.get('owner'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        requestid=lambda x: x.get('requestid'))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
