# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from copy import deepcopy

from sqlalchemy import MetaData
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import UnicodeText
from sqlalchemy import Unicode
from sqlalchemy import Table

from sqlalchemy.schema import ForeignKeyConstraint

from sqlalchemy.types import TIMESTAMP

from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import object_session

from sqlalchemy.ext.declarative import declarative_base

import sbds.logging

from sbds.utils import Vividict

from sbds.storages.db import prepare_raw_block
from sbds.storages.db import extract_operations_from_block
from sbds.storages.db import extract_transactions_from_block

from sbds.storages.db.tables.enums import transaction_types_enum

from sbds.storages.db.tables.field_handlers import json_metadata
from sbds.storages.db.tables.field_handlers import amount
from sbds.storages.db.tables.field_handlers import amount_symbol
from sbds.storages.db.tables.field_handlers import comment_body


from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session


from sbds.storages.db.tables import Transaction
from sbds.storages.db.tables.transaction_classes import TxComment

logger = sbds.logging.getLogger(__name__)



class BasePostComment(Base):
    __tablename__ = 'None'
    __table_args__ = (
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_general_ci'
            }
    )
    id = Column(Integer, primary_key=True)
    tx_comment_id = Column(ForeignKey(TxComment.id,
                                      use_alter=True,
                                      onupdate='CASCADE',
                                      ondelete='CASCADE'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('Account.id'), nullable=False, index=True)

    timestamp = Column(DateTime(timezone=False))
    permlink = Column(Unicode(512), nullable=False, index=True)
    title = Column(Unicode(250))
    body = Column(UnicodeText)
    json_metadata = Column(UnicodeText)

    author = relationship('Account', backref='posts')
    txcomment = relationship('TxComment')


    _fields = dict()


    def __repr__(self):
        return "<%s (%s)>" % (self.__name__, self.__dict__)

    @classmethod
    def from_txcomment(cls, txcomment, **kwargs):
        pass

    @classmethod
    def _prepare_for_storage(cls, **kwargs):
        data_dict = Vividict(kwargs['data_dict'])
        op_type = data_dict['type']
        _fields = cls._fields
        try:
            prepared = {k: v(data_dict) for k, v in _fields.items()}
            if data_dict['remove_empty']:
                prepared = {k: v for k, v in prepared.items() if v}
            if 'transaction_obj' in kwargs:
                prepared['transaction'] = kwargs['transaction_obj']
            elif 'tx_id' in kwargs:
                prepared['tx_id'] = kwargs['tx_id']
            return prepared
        except Exception as e:
            extra = dict(op_type=op_type, data_dict=data_dict, _fields=_fields, error=e, **kwargs)
            logger.error(e, extra=extra)
            return None

class Post(Base):
    tags = relationship("Tag", secondary='post_tag_table', backref='posts')


    _fields = dict(
            author=lambda x: x['author'],
            permlink=lambda x: x['permlink'],
            title=lambda x: x['title'],
            body=lambda x: comment_body(x['body']),
            json_metadata=lambda x: json_metadata(x['json_metadata']),
    )

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'employee'
    }

class Comment(Base):
    """
    Raw Format
    ==========
    {
        "ref_block_prefix": 3071757153,
        "operations": [
            [
                "comment",
                {
                    "author": "xeldal",
                    "body": "This is xeldal, an experienced witness. Will you vote for me?",
                    "json_metadata": "{}",
                    "title": "xeldal Witness Thread",
                    "permlink": "xeldal-witness-post",
                    "parent_author": "",
                    "parent_permlink": "witness-category"
                }
            ]
        ],
        "signatures": [
            "1f332f851112774103c4a12a97941f1c39a1c30a0561e64fbbe756d0860f7e68a206f2f57dfd15b77ecf3ce13fcffd6e66ae4b65a8df29bc01682876e34eb3cecf"
        ],
        "ref_block_num": 32379,
        "expiration": "2016-04-08T16:20:27",
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "tx_id": 44351,
        "author": "xeldal",
        "body": "This is xeldal, an experienced witness. Will you vote for me?",
        "parent_permlink": "witness-category",
        "title": "xeldal Witness Thread",
        "permlink": "xeldal-witness-post",
        "id": 25,
        "parent_author": "",
        "json_metadata": "{}"
    }
    """

    __tablename__ = 'Comments'
    __table_args__ = (
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_general_ci'
        }
    )

    post_id = Column(Integer, ForeignKey('Post.id'), nullable=False, index=True)

    parent_comments = relationship("Comment", remote_side=[id])
    child_comments = relationship("Comment", backref=backref('parent', remote_side=[id]))
    post = relationship("Post", backref='comments' )
    tags = relationship("Tag", secondary='comment_tag_table', backref='posts')

    _fields = dict(
            author=lambda x: x['author'],
            permlink=lambda x: x['permlink'],
            title=lambda x: x['title'],
            body=lambda x: comment_body(x['body']),
            json_metadata=lambda x: json_metadata(x['json_metadata']),
    )



class Account(Base):
    __tablename__ = 'Comments'
    __table_args__ = (
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_general_ci'
        }
    )

    _fields = dict(
            author=lambda x: x['author'],
            permlink=lambda x: x['permlink'],
            title=lambda x: x['title'],
            body=lambda x: comment_body(x['body']),
            json_metadata=lambda x: json_metadata(x['json_metadata']),
    )



class Tag(Base):
    __tablename__ = 'Tag'
    __table_args__ = (
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_general_ci'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime(timezone=False))

    _fields = dict(created=lambda x: x['created'])


post_tag_table = Table('post_tag_table', Base.metadata,
    Column('post_id', Integer, ForeignKey('Post.id')),
    Column('tag_id', Integer, ForeignKey('Tag.id'))
)

comment_tag_table = Table('comment_tag_table', Base.metadata,
    Column('comment_id', Integer, ForeignKey('Comment.id')),
    Column('tag_id', Integer, ForeignKey('Tag.id'))
)