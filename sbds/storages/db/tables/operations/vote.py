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

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class VoteOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "voter": "steemit78",
      "permlink": "firstpost",
      "author": "steemit",
      "weight": 10000
    }

    

    """
    
    __tablename__ = 'sbds_op_votes'
    __operation_type__ = 'vote_operation'
    
    voter = Column(String(50), index=True) # steem_type:account_name_type
    author = Column(String(50), index=True) # steem_type:account_name_type
    permlink = Column(Unicode(512), index=True) # name:permlink
    weight = Column(SmallInteger) # steem_type:int16_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='vote_operation')
    
    _fields = dict(
        voter=lambda x: x.get('voter'),
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        weight=lambda x: x.get('weight'),
    )

