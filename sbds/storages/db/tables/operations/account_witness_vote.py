# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field


class AccountWitnessVoteOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "account": "donalddrumpf",
      "approve": true,
      "witness": "berniesanders"
    }



    """

    __tablename__ = 'sbds_op_account_witness_votes'
    __table_args__ = (ForeignKeyConstraint(
        ['account'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        ForeignKeyConstraint(
        ['witness'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        Index(
        'ix_sbds_sbds_op_account_witness_votes_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True),
        Index(
        'ix_sbds_op_account_witness_votes_accounts',
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

    account = Column(Text, nullable=True)  # steem_type:account_name_type
    witness = Column(Text, nullable=True)  # steem_type:account_name_type
    approve = Column(Boolean)  # steem_type:bool
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        accounts=lambda x: accounts_field(x, 'account_witness_vote'), )

    _account_fields = frozenset([
        'account',
        'witness',
    ])
