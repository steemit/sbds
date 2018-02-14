
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

class InterestOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct interest_operation : public virtual_operation
   {
      interest_operation( const string& o = "", const asset& i = asset(0,SBD_SYMBOL) )
         :owner(o),interest(i){}

      account_name_type owner;
      asset             interest;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_interest_operations'
    __operation_type__ = 'interest_operation'
    
    owner = Column(Unicode(50))
    interest = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        owner=lambda x: x.get('owner'),
        interest=lambda x: amount_field(x.get('interest'), num_func=float),
    )

