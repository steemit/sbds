# -*- coding: utf-8 -*-

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
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation


class CommentOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "title": "Welcome to Steem!",
      "parent_permlink": "meta",
      "permlink": "firstpost",
      "parent_author": "",
      "body": "Steemit is a social media platform where anyone can earn STEEM points by posting. The more people who like a post, the more STEEM the poster earns. Anyone can sell their STEEM for cash or vest it to boost their voting power.",
      "json_metadata": "",
      "author": "steemit"
    }



    """

    __tablename__ = 'sbds_op_comments'
    __operation_type__ = 'comment_operation'

    parent_author = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    parent_permlink = Column(Unicode(512), index=True)  # name:parent_permlink
    author = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    permlink = Column(Unicode(512), index=True)  # name:permlink
    title = Column(Unicode(512), index=True)  # name:title,comment_operation
    body = Column(UnicodeText)  # name:body
    json_metadata = Column(JSONB)  # name:json_metadata
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='comment_operation')

    _fields = dict(
        body=lambda x: comment_body_field(x.get('body')),
    )
