
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

class HardforkOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct hardfork_operation : public virtual_operation
   {
      hardfork_operation() {}
      hardfork_operation( uint32_t hf_id ) : hardfork_id( hf_id ) {}

      uint32_t         hardfork_id = 0;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_hardfork_operations'
    __operation_type__ = 'hardfork_operation'
    
    hardfork_id = Column(Unicode(100))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        hardfork_id=lambda x: x.get('hardfork_id'),
    )

