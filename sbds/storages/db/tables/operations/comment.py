# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import func

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import comment_body_field
from .base import BaseOperation


class CommentOperation(Base, BaseOperation):
    """Raw Format
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

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_comments'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    author = Column(Unicode(50), nullable=False, index=True)
    permlink = Column(Unicode(512), nullable=False, index=True)
    parent_author = Column(Unicode(50), index=True)
    parent_permlink = Column(Unicode(512))
    title = Column(Unicode(512))
    body = Column(UnicodeText)
    json_metadata = Column(UnicodeText)

    _fields = dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        parent_author=lambda x: x.get('parent_author'),
        parent_permlink=lambda x: x.get('parent_permlink'),
        title=lambda x: x.get('title'),
        body=lambda x: comment_body_field(x['body']),
        json_metadata=lambda x: x.get('json_metadata'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)

    @classmethod
    def find_parent_from_prepared(cls, session, prepared):
        return session.query(cls).filter(
            cls.parent_permlink == prepared['parent_permlink'],
            cls.parent_author == prepared['parent_author']).one_or_none()

    @classmethod
    def post_filter(cls, query):
        return query.filter(cls.parent_author == '')

    @classmethod
    def comment_filter(cls, query):
        return query.filter(cls.parent_author != '')

    @classmethod
    def count_query(cls, session):
        return session.query(func.count(cls.block_num))

    @classmethod
    def post_count_query(cls, session):
        count_query = cls.count_query(session)
        return cls.post_filter(count_query)

    @classmethod
    def comment_count_query(cls, session):
        count_query = cls.count_query(session)
        return cls.comment_filter(count_query)

    @property
    def type(self):
        # include self.author to assure decision isn't made on a blank instance
        if all([self.author, self.parent_author]):
            return 'comment'
        elif self.author and not self.parent_author:
            return 'post'

    @property
    def is_post(self):
        return self.type == 'post'

    @property
    def is_comment(self):
        return self.type == 'comment'
