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


class AccountCreateOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "creator": "hello",
      "json_metadata": "{}",
      "owner": {
        "key_auths": [
          [
            "STM8MN3FNBa8WbEpxz3wGL3L1mkt6sGnncH8iuto7r8Wa3T9NSSGT",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      },
      "memo_key": "STM6Gkj27XMkoGsr4zwEvkjNhh4dykbXmPFzHhT8g86jWsqu3U38X",
      "fee": "0.000 STEEM",
      "active": {
        "key_auths": [
          [
            "STM8HCf7QLUexogEviN8x1SpKRhFwg2sc8LrWuJqv7QsmWrua6ZyR",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      },
      "posting": {
        "key_auths": [
          [
            "STM8EhGWcEuQ2pqCKkGHnbmcTNpWYZDjGTT7ketVBp4gUStDr2brz",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      },
      "new_account_name": "fabian"
    }



    """

    __tablename__ = 'sbds_op_account_creates'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['creator'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),



        ForeignKeyConstraint(['new_account_name'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_account_creates_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(ARRAY(String(16)))
    fee = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    fee_symbol = Column(String(5))  # steem_type:asset
    creator = Column(String(16), nullable=True)  # steem_type:account_name_type
    new_account_name = Column(String(16), nullable=True)  # steem_type:account_name_type
    owner = Column(JSONB)  # steem_type:authority
    active = Column(JSONB)  # steem_type:authority
    posting = Column(JSONB)  # steem_type:authority
    memo_key = Column(String(60), nullable=False)  # steem_type:public_key_type
    json_metadata = Column(JSONB)  # name:json_metadata
    operation_type = Column(operation_types_enum, nullable=False, default='account_create')

    _fields = dict(
        fee=lambda x: amount_field(x.get('fee'), num_func=float),  # steem_type:asset
        fee_symbol=lambda x: amount_symbol_field(x.get('fee')),  # steem_type:asset
        owner=lambda x: json_string_field(x.get('owner')),  # steem_type:authority
        active=lambda x: json_string_field(x.get('active')),  # name:active
        posting=lambda x: json_string_field(x.get('posting')),  # name:posting
        json_metadata=lambda x: json_string_field(x.get('json_metadata')),  # name:json_metadata
        accounts=lambda x: tuple(flatten((x.get('creator'), x.get('new_account_name'),)))
    )

    _account_fields = frozenset(['creator', 'new_account_name', ])
