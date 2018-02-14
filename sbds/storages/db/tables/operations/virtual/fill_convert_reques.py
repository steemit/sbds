
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

class FillConvertRequestOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct fill_convert_request_operation : public virtual_operation
   {
      fill_convert_request_operation(){}
      fill_convert_request_operation( const string& o, const uint32_t id, const asset& in, const asset& out )
         :owner(o), requestid(id), amount_in(in), amount_out(out) {}

      account_name_type owner;
      uint32_t          requestid = 0;
      asset             amount_in;
      asset             amount_out;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_fill_convert_request_operations'
    __operation_type__ = 'fill_convert_request_operation'
    
    owner = Column(Unicode(50))
    requestid = Column(Unicode(100))
    amount_in = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    amount_out = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        owner=lambda x: x.get('owner'),
        requestid=lambda x: x.get('requestid'),
        amount_in=lambda x: amount_field(x.get('amount_in'), num_func=float),
        amount_out=lambda x: amount_field(x.get('amount_out'), num_func=float),
    )

