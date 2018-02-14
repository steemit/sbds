
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

class FillOrderOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct fill_order_operation : public virtual_operation
   {
      fill_order_operation(){}
      fill_order_operation( const string& c_o, uint32_t c_id, const asset& c_p, const string& o_o, uint32_t o_id, const asset& o_p )
      :current_owner(c_o), current_orderid(c_id), current_pays(c_p), open_owner(o_o), open_orderid(o_id), open_pays(o_p) {}

      account_name_type current_owner;
      uint32_t          current_orderid = 0;
      asset             current_pays;
      account_name_type open_owner;
      uint32_t          open_orderid = 0;
      asset             open_pays;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_fill_order_operations'
    __operation_type__ = 'fill_order_operation'
    
    current_owner = Column(Unicode(50))
    current_orderid = Column(Unicode(100))
    current_pays = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    open_owner = Column(Unicode(50))
    open_orderid = Column(Unicode(100))
    open_pays = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        current_owner=lambda x: x.get('current_owner'),
        current_orderid=lambda x: x.get('current_orderid'),
        current_pays=lambda x: amount_field(x.get('current_pays'), num_func=float),
        open_owner=lambda x: x.get('open_owner'),
        open_orderid=lambda x: x.get('open_orderid'),
        open_pays=lambda x: amount_field(x.get('open_pays'), num_func=float),
    )

