# -*- coding: utf-8 -*-
import dateutil.parser

from funcy import flatten
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
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import Index
from sqlalchemy import ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from toolz.dicttoolz import dissoc

import sbds.sbds_json

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field


class CommentOperation(Base):
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
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['parent_author'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),



        ForeignKeyConstraint(['author'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_comments_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(ARRAY(String(16)))
    parent_author = Column(String(16), nullable=True)  # steem_type:account_name_type
    parent_permlink = Column(Unicode(256), index=True)  # name:parent_permlink
    author = Column(String(16), nullable=True)  # steem_type:account_name_type
    permlink = Column(Unicode(256), index=True)  # name:permlink
    title = Column(Unicode(256), index=True)  # name:title,comment_operation
    body = Column(UnicodeText)  # name:body
    json_metadata = Column(JSONB)  # name:json_metadata
    operation_type = Column(operation_types_enum, nullable=False, default='comment')

    _fields = dict(
        body=lambda x: comment_body_field(x.get('body')),  # name:body
        json_metadata=lambda x: json_string_field(x.get('json_metadata')),  # name:json_metadata
        accounts=lambda x: tuple(flatten((x.get('parent_author'), x.get('author'),)))
    )

    _account_fields = frozenset(['parent_author', 'author', ])
