# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UnicodeText
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import asset_types_enum
from ...enums import operation_types_enum
from ...field_handlers import accounts_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field


class TransferToSavingsOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "from": "abit",
      "to": "abit",
      "amount": "1.000 SBD",
      "memo": ""
    }



    """

    __tablename__ = 'sbds_op_transfer_to_saving'
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
        Index(
        'ix_sbds_sbds_op_transfer_to_saving_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True),
        Index(
        'ix_sbds_op_transfer_to_saving_accounts',
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
    amount = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    amount_symbol = Column(
        asset_types_enum, nullable=False)  # steem_type:asset
    memo = Column(UnicodeText)  # name:memo
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        amount=lambda x: amount_field(x.get('amount'), num_func=float),  # steem_type:asset
        amount_symbol=lambda x: amount_symbol_field(x.get('amount')),  # steem_type:asset
        accounts=lambda x: accounts_field(x, 'transfer_to_savings'),
    )

    _account_fields = frozenset([
        'from',
        'to',
    ])
