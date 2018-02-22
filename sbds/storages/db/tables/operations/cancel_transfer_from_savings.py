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

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class CancelTransferFromSavingsOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "from": "jesta",
      "request_id": 1
    }

    

    """
    
    __tablename__ = 'sbds_op_cancel_transfer_from_saving'
    __operation_type__ = 'cancel_transfer_from_savings_operation'
    
    _from = Column('from', Unicode(50), index=True) # name:from
    request_id = Column(Integer) # steem_type:uint32_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='cancel_transfer_from_savings_operation')
    
    _fields = dict(
        _from=lambda x: x.get('from'),
        request_id=lambda x: x.get('request_id'),
    )


