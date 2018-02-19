# coding=utf-8
import os.path

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean
from sqlalchemy import SmallInteger
from sqlalchemy import Integer
from sqlalchemy import BigInteger

from sqlalchemy.dialects.mysql import JSON

from toolz import get_in

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class ClaimRewardBalanceOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "reward_steem": "0.017 STEEM",
      "reward_vests": "185.025103 VESTS",
      "account": "ocrdu",
      "reward_sbd": "0.011 SBD"
    }

    

    """
    
    __tablename__ = 'sbds_op_claim_reward_balances'
    __operation_type__ = 'claim_reward_balance_operation'
    
    account = Column(String(50), index=True) # steem_type:account_name_type
    reward_steem = Column(Numeric(20,6), nullable=False) # steem_type:asset
    reward_steem_symbol = Column(String(5)) # steem_type:asset
    reward_sbd = Column(Numeric(20,6), nullable=False) # steem_type:asset
    reward_sbd_symbol = Column(String(5)) # steem_type:asset
    reward_vests = Column(Numeric(20,6), nullable=False) # steem_type:asset
    reward_vests_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='claim_reward_balance_operation')
    
    _fields = dict(
        account=lambda x: x.get('account'),
        reward_steem=lambda x: amount_field(x.get('reward_steem'), num_func=float),
        reward_steem_symbol=lambda x: amount_symbol_field(x.get('reward_steem')),
        reward_sbd=lambda x: amount_field(x.get('reward_sbd'), num_func=float),
        reward_sbd_symbol=lambda x: amount_symbol_field(x.get('reward_sbd')),
        reward_vests=lambda x: amount_field(x.get('reward_vests'), num_func=float),
        reward_vests_symbol=lambda x: amount_symbol_field(x.get('reward_vests')),
    )

