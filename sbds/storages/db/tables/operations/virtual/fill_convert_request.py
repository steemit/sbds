# coding=utf-8

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

#from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import JSON

from ...import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field
from ..base import BaseOperation
from ..base import BaseVirtualOperation

class FillConvertRequestOperation(Base, BaseVirtualOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_virtual_fill_convert_requests'
    __operation_type__ = 'fill_convert_request_operation'
    
    owner = Column(JSONB) # name:owner
    requestid = Column(Integer) # steem_type:uint32_t
    amount_in = Column(Numeric(20,6), nullable=False) # steem_type:asset
    amount_in_symbol = Column(String(5)) # steem_type:asset
    amount_out = Column(Numeric(20,6), nullable=False) # steem_type:asset
    amount_out_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='fill_convert_request_operation')
    
    _fields = dict(
        owner=lambda x: x.get('owner'),
        requestid=lambda x: x.get('requestid'),
        amount_in=lambda x: amount_field(x.get('amount_in'), num_func=float),
        amount_in_symbol=lambda x: amount_symbol_field(x.get('amount_in')),
        amount_out=lambda x: amount_field(x.get('amount_out'), num_func=float),
        amount_out_symbol=lambda x: amount_symbol_field(x.get('amount_out')),
    )


