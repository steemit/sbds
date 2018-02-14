
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

class FillVestingWithdrawOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
       struct fill_vesting_withdraw_operation : public virtual_operation
   {
      fill_vesting_withdraw_operation(){}
      fill_vesting_withdraw_operation( const string& f, const string& t, const asset& w, const asset& d )
         :from_account(f), to_account(t), withdrawn(w), deposited(d) {}

      account_name_type from_account;
      account_name_type to_account;
      asset             withdrawn;
      asset             deposited;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_fill_vesting_withdraw_operations'
    __operation_type__ = 'fill_vesting_withdraw_operation'
    
    from_account = Column(Unicode(50))
    to_account = Column(Unicode(50))
    withdrawn = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    deposited = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        from_account=lambda x: x.get('from_account'),
        to_account=lambda x: x.get('to_account'),
        withdrawn=lambda x: amount_field(x.get('withdrawn'), num_func=float),
        deposited=lambda x: amount_field(x.get('deposited'), num_func=float),
    )

