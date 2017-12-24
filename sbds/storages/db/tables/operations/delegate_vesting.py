# coding=utf-8

import os.path


import os.path
from sqlalchemy import Column, Unicode, Numeric, Enum

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class DelegateVestingSharesOperation(Base, BaseOperation):
    """
    {
      "ref_block_num": 13361,
      "ref_block_prefix": 1969744882,
      "expiration": "2017-03-30T15:39:45",
      "operations": [
        [
          "delegate_vesting_shares",
          {
            "delegator": "liberosist",
            "delegatee": "dunia",
            "vesting_shares": "94599167.138276 VESTS"
          }
        ]
      ],
      "extensions": [],
      "signatures": [
        "2058ca7ba73a5787be2b5cf62595251279de63344709240f6300a8625f0f26cc550fa5b3ce740220b085c7b539f6b822047d4136cafc8245f60bcca5822d929f8a"
      ]
    }
    """

    __tablename__ = 'sbds_op_delegate_vesting_shares'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    delegator = Column(Unicode(50), index=True)
    delegatee = Column(Unicode(50), index=True)
    vesting_shares = Column(Numeric(15, 6))

    _fields = dict(
        delegator=lambda x: x.get('delegator'),
        delegatee=lambda x: x.get('delegatee'),
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float)
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

