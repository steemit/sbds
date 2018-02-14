
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

class ShutdownWitnessOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
       struct shutdown_witness_operation : public virtual_operation
   {
      shutdown_witness_operation(){}
      shutdown_witness_operation( const string& o ):owner(o) {}

      account_name_type owner;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_shutdown_witness_operations'
    __operation_type__ = 'shutdown_witness_operation'
    
    owner = Column(Unicode(50))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        owner=lambda x: x.get('owner'),
    )

