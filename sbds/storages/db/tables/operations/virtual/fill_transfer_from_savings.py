
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

class FillTransferFromSavingsOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct fill_transfer_from_savings_operation : public virtual_operation
   {
      fill_transfer_from_savings_operation() {}
      fill_transfer_from_savings_operation( const account_name_type& f, const account_name_type& t, const asset& a, const uint32_t r, const string& m )
         :from(f), to(t), amount(a), request_id(r), memo(m) {}

      account_name_type from;
      account_name_type to;
      asset             amount;
      uint32_t          request_id = 0;
      string            memo;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_fill_transfer_from_savings_operations'
    __operation_type__ = 'fill_transfer_from_savings_operation'
    
    from = Column(Unicode(50))
    to = Column(Unicode(50))
    amount = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    request_id = Column(Unicode(100))
    memo = Column(Unicode(150))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        request_id=lambda x: x.get('request_id'),
        memo=lambda x: x.get('memo'),
    )

