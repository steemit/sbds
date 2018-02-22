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

class FillOrderOperation(Base, BaseVirtualOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_virtual_fill_orders'
    __operation_type__ = 'fill_order_operation'
    
    current_owner = Column(String(50), index=True) # steem_type:account_name_type
    current_orderid = Column(Integer) # steem_type:uint32_t
    current_pays = Column(Numeric(20,6), nullable=False) # steem_type:asset
    current_pays_symbol = Column(String(5)) # steem_type:asset
    open_owner = Column(String(50), index=True) # steem_type:account_name_type
    open_orderid = Column(Integer) # steem_type:uint32_t
    open_pays = Column(Numeric(20,6), nullable=False) # steem_type:asset
    open_pays_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='fill_order_operation')
    
    _fields = dict(
        current_owner=lambda x: x.get('current_owner'),
        current_orderid=lambda x: x.get('current_orderid'),
        current_pays=lambda x: amount_field(x.get('current_pays'), num_func=float),
        current_pays_symbol=lambda x: amount_symbol_field(x.get('current_pays')),
        open_owner=lambda x: x.get('open_owner'),
        open_orderid=lambda x: x.get('open_orderid'),
        open_pays=lambda x: amount_field(x.get('open_pays'), num_func=float),
        open_pays_symbol=lambda x: amount_symbol_field(x.get('open_pays')),
    )


