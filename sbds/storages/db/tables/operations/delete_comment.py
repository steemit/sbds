# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field


class DeleteCommentOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "permlink": "test-delete",
      "author": "jsc"
    }



    """

    __tablename__ = 'sbds_op_delete_comments'
    __table_args__ = (ForeignKeyConstraint(
        ['author'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        UniqueConstraint('block_num', 'transaction_num',
                         'operation_num', 'raw'),
        Index(
        'ix_sbds_op_delete_comments_accounts',
        'accounts',
        postgresql_using='gin',
        postgresql_ops={'accounts': 'jsonb_path_ops'}))

    _id = Column(BigInteger, autoincrement=True, primary_key=True)
    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(Text, nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    author = Column(Text, nullable=True)  # steem_type:account_name_type
    permlink = Column(UnicodeText, index=True)  # name:permlink
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(accounts=lambda x: accounts_field(x, 'delete_comment'), )

    _account_fields = frozenset([
        'author',
    ])
