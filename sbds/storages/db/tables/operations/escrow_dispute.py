
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

class EscrowDisputeOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "who": "anonymtest",
      "from": "anonymtest",
      "to": "someguy123",
      "escrow_id": 72526562,
      "agent": "xtar"
    }
    

    """
    
    __tablename__ = 'sbds_op_escrow_disputes'
    __operation_type__ = 'escrow_dispute_operation'
    
    _from = Column('from', Unicode(50), index=True) # name:from
    to = Column(String(50), index=True) # steem_type:account_name_type
    agent = Column(String(50), index=True) # steem_type:account_name_type
    who = Column(String(50), index=True) # steem_type:account_name_type
    escrow_id = Column(Integer) # steem_type:uint32_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='escrow_dispute_operation')
    
    _fields = dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        who=lambda x: x.get('who'),
        escrow_id=lambda x: x.get('escrow_id'),
    )

