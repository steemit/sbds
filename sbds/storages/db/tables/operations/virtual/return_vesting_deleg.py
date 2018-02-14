
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

class ReturnVestingDelegationOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct return_vesting_delegation_operation : public virtual_operation
   {
      return_vesting_delegation_operation() {}
      return_vesting_delegation_operation( const account_name_type& a, const asset& v ) : account( a ), vesting_shares( v ) {}

      account_name_type account;
      asset             vesting_shares;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_return_vesting_delegation_operations'
    __operation_type__ = 'return_vesting_delegation_operation'
    
    account = Column(Unicode(50))
    vesting_shares = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        account=lambda x: x.get('account'),
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float),
    )

