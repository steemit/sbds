# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field


class EscrowApproveOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "who": "on0tole",
      "approve": true,
      "from": "xtar",
      "agent": "on0tole",
      "to": "testz",
      "escrow_id": 59102208
    }



    """

    __tablename__ = 'sbds_op_escrow_approves'
    __table_args__ = (ForeignKeyConstraint(
        ['from'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        ForeignKeyConstraint(
        ['to'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        ForeignKeyConstraint(
        ['agent'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        ForeignKeyConstraint(
        ['who'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        UniqueConstraint('block_num', 'transaction_num',
                         'operation_num', 'raw'),
        Index(
        'ix_sbds_op_escrow_approves_accounts',
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

    _from = Column('from', UnicodeText)  # name:from
    to = Column(Text, nullable=True)  # steem_type:account_name_type
    agent = Column(Text, nullable=True)  # steem_type:account_name_type
    who = Column(Text, nullable=True)  # steem_type:account_name_type
    escrow_id = Column(Numeric)  # steem_type:uint32_t
    approve = Column(Boolean)  # steem_type:bool
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(accounts=lambda x: accounts_field(x, 'escrow_approve'), )

    _account_fields = frozenset([
        'from',
        'to',
        'agent',
        'who',
    ])
