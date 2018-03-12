# -*- coding: utf-8 -*-

import dateutil.parser
import rapidjson

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
from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import JSONB

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
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

    voter = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    author = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    permlink = Column(Unicode(256), index=True) # name:permlink
    weight = Column(SmallInteger) # steem_type:int16_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='vote')

    _fields = dict(

    )


