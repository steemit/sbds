
# coding=utf-8
import os.path

from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from toolz import get_in

from ... import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ..base import BaseOperation

class LiquidityRewardOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct liquidity_reward_operation : public virtual_operation
   {
      liquidity_reward_operation( string o = string(), asset p = asset() )
      :owner(o), payout(p) {}

      account_name_type owner;
      asset             payout;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_liquidity_reward_operations'
    __operation_type__ = 'liquidity_reward_operation'
    
    owner = Column(Unicode(50))
    payout = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        owner=lambda x: x.get('owner'),
        payout=lambda x: amount_field(x.get('payout'), num_func=float),
    )

