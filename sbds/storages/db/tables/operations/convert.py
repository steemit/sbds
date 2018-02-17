
# coding=utf-8
import os.path

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

from sqlalchemy.dialects.mysql import JSON

from toolz import get_in

from ... import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field
from ..base import BaseOperation

class ConvertOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "amount": "5.000 SBD",
      "requestid": 1467592156,
      "owner": "summon"
    }
    

    """
    
    __tablename__ = 'sbds_op_converts'
    __operation_type__ = 'convert_operation'
    
    owner = Column(JSON) # name:owner
    requestid = Column(Integer) # steem_type:uint32_t
    amount = Column(Numeric(15,6), nullable=False) # steem_type:asset
    amount_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='convert_operation')
    
    _fields = dict(
        owner=lambda x: x.get('owner'),
        requestid=lambda x: x.get('requestid'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x.get('amount')),
    )

