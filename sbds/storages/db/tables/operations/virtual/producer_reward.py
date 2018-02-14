
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

class ProducerRewardOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct producer_reward_operation : public virtual_operation
   {
      producer_reward_operation(){}
      producer_reward_operation( const string& p, const asset& v ) : producer( p ), vesting_shares( v ) {}

      account_name_type producer;
      asset             vesting_shares;

   };
    
    
    """
    
    __tablename__ = 'sbds_op_producer_reward_operations'
    __operation_type__ = 'producer_reward_operation'
    
    producer = Column(Unicode(50))
    vesting_shares = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        producer=lambda x: x.get('producer'),
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float),
    )

