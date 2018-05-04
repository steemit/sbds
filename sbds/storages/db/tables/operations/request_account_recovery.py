# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
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
from ...field_handlers import json_string_field


class RequestAccountRecoveryOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "new_owner_authority": {
        "key_auths": [
          [
            "STM6LYxj96zdypHYqgDdD6Nyh2NxerN3P1Mp3ddNm7gci63nfrSuZ",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      },
      "account_to_recover": "gandalf",
      "recovery_account": "steem",
      "extensions": []
    }



    """

    __tablename__ = 'sbds_op_request_account_recoveries'
    __table_args__ = (ForeignKeyConstraint(
        ['recovery_account'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        ForeignKeyConstraint(
        ['account_to_recover'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        Index(
        'ix_sbds_sbds_op_request_account_recoveries_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True),
        Index(
        'ix_sbds_op_request_account_recoveries_accounts',
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

    recovery_account = Column(
        Text, nullable=True)  # steem_type:account_name_type
    account_to_recover = Column(
        Text, nullable=True)  # steem_type:account_name_type
    new_owner_authority = Column(JSONB)  # steem_type:authority
    extensions = Column(JSONB)  # steem_type:extensions_type
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        new_owner_authority=lambda x: json_string_field(
            x.get('new_owner_authority')),  # steem_type:authority
        extensions=lambda x: json_string_field(x.get('extensions')),  # steem_type:extensions_type
        accounts=lambda x: accounts_field(x, 'request_account_recovery'),
    )

    _account_fields = frozenset([
        'recovery_account',
        'account_to_recover',
    ])
