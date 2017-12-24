# coding=utf-8

import os.path


import os.path
from sqlalchemy import Column, Unicode, Numeric, Enum

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class ClaimRewardBalanceOperation(Base, BaseOperation):
    """


    Args:

    Returns:

    {
      "ref_block_num": 18849,
      "ref_block_prefix": 3618600471,
      "expiration": "2017-03-30T20:15:54",
      "operations": [
        [
          "claim_reward_balance",
          {
            "account": "ocrdu",
            "reward_steem": "0.017 STEEM",
            "reward_sbd": "0.011 SBD",
            "reward_vests": "185.025103 VESTS"
          }
        ]
      ],
      "extensions": [],
      "signatures": [
        "2074300e7bc9064b7aa47fe14be844d53737e0981daa7c2b5a3a1c3ffe884ea1866d62bc5d16230495536492ab62493c483f484d67422d25a7d18078d10ca740fb"
      ]
    }


    """

    __tablename__ = 'sbds_op_claim_reward_balances'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    account = Column(Unicode(50), index=True, nullable=False)
    reward_steem = Column(Numeric(15, 6))
    reward_sbd = Column(Numeric(15, 6))
    reward_vests = Column(Numeric(15, 6))

    _fields = dict(
        account=lambda x: x.get('account'),
        reward_steem=lambda x: amount_field(x.get('reward_steem'), num_func=float),
        reward_sbd=lambda x: amount_field(x.get('reward_sbd'), num_func=float),
        reward_vests=lambda x: amount_field(x.get('reward_vests'), num_func=float)
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

