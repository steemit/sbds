
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
    
    parent_author = Column(String(50), index=True) # steem_type:account_name_type
    parent_permlink = Column(Unicode(150)) # steem_type:string
    author = Column(String(50), index=True) # steem_type:account_name_type
    permlink = Column(Unicode(150)) # steem_type:string
    title = Column(Unicode(150)) # steem_type:string
    body = Column(UnicodeText) # name:body
    json_metadata = Column(JSON) # name:json_metadata
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='comment_operation')
    
    _fields = dict(
        parent_author=lambda x: x.get('parent_author'),
        parent_permlink=lambda x: x.get('parent_permlink'),
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        title=lambda x: x.get('title'),
        body=lambda x: comment_body_field(x.get('body')),
        json_metadata=lambda x: x.get('json_metadata'),
    )

