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

class FeedPublishOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "exchange_rate": {
        "quote": "1000.000 STEEM",
        "base": "1.000 SBD"
      },
      "publisher": "abit"
    }

    

    """
    
    __tablename__ = 'sbds_op_feed_publishes'
    __operation_type__ = 'feed_publish_operation'
    
    publisher = Column(String(50), index=True) # steem_type:account_name_type
    exchange_rate = Column(JSON) # steem_type:price
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='feed_publish_operation')
    
    _fields = dict(
        publisher=lambda x: x.get('publisher'),
        exchange_rate=lambda x: x.get('exchange_rate'),
    )


