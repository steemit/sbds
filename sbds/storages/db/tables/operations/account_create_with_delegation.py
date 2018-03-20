# -*- coding: utf-8 -*-
import dateutil.parser


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
from sqlalchemy.dialects.postgresql import JSONB
from toolz.dicttoolz import dissoc

import sbds.sbds_json

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field


class AccountCreateWithDelegationOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "delegation": "0.000000 VESTS",
      "owner": {
        "key_auths": [
          [
            "STM51YSoy7MdrAWgeTsQo4xYVR7L4BKucjqDPefsB7ZojBZgU7CCN",
            1
          ]
        ],
        "weight_threshold": 1,
        "account_auths": []
      },
      "active": {
        "key_auths": [
          [
            "STM5jgwX1VPT4oZpescjwTmf6k8T8oYmg3RrhjaDnSapis9sFojAL",
            1
          ]
        ],
        "weight_threshold": 1,
        "account_auths": []
      },
      "creator": "steem",
      "posting": {
        "key_auths": [
          [
            "STM5BcLMqLSBXa3DX7ThbbDYFEwcHbvUYWoF8PgTaSVAdNUikBQK1",
            1
          ]
        ],
        "weight_threshold": 1,
        "account_auths": []
      },
      "json_metadata": "",
      "extensions": [],
      "new_account_name": "hendratayogas",
      "fee": "35.000 STEEM",
      "memo_key": "STM5Fj3bNfLCvhFC6U67kfNCg6d8CfpxW2AJRJ9KhELEaoBMK9Ltf"
    }

    """

    __tablename__ = 'sbds_op_account_create_with_delegations'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),
        ForeignKeyConstraint(['creator'], ['sbds_meta_accounts.name'],
            deferrable=True, initially='DEFERRED', use_alter=True),
        ForeignKeyConstraint(['new_account_name'], ['sbds_meta_accounts.name'],
            deferrable=True, initially='DEFERRED', use_alter=True),)

    
    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False, index=True)
    operation_num = Column(SmallInteger, nullable=False, index=True)
    trx_id = Column(String(40),nullable=False)
    timestamp = Column(DateTime(timezone=False))
    fee = Column(Numeric(20,6), nullable=False) # steem_type:asset
    fee_symbol = Column(String(5)) # steem_type:asset
    delegation = Column(Numeric(20,6), nullable=False) # steem_type:asset
    delegation_symbol = Column(String(5)) # steem_type:asset
    creator = Column(String(16)) # steem_type:account_name_type
    new_account_name = Column(String(16)) # steem_type:account_name_type
    owner = Column(JSONB) # steem_type:authority
    active = Column(JSONB) # steem_type:authority
    posting = Column(JSONB) # steem_type:authority
    memo_key = Column(String(60), nullable=False) # steem_type:public_key_type
    json_metadata = Column(JSONB) # name:json_metadata
    extensions = Column(JSONB) # steem_type:extensions_type
    operation_type = Column(operation_types_enum,nullable=False,index=True,default='account_create_with_delegation')


    _fields = dict(
        fee=lambda x: amount_field(x.get('fee'), num_func=float), # steem_type:asset
        fee_symbol=lambda x: amount_symbol_field(x.get('fee')), # steem_type:asset
        delegation=lambda x: amount_field(x.get('delegation'), num_func=float), # steem_type:asset
        delegation_symbol=lambda x: amount_symbol_field(x.get('delegation')), # steem_type:asset
        owner=lambda x:json_string_field(x.get('owner')), # steem_type:authority
        active=lambda x: json_string_field(x.get('active')), # name:active
        posting=lambda x: json_string_field(x.get('posting')), # name:posting
        json_metadata=lambda x: json_string_field(x.get('json_metadata')), # name:json_metadata
        extensions=lambda x:json_string_field(x.get('extensions')), # steem_type:extensions_type
        
    )

    _account_fields = frozenset(['creator','new_account_name',])

    def dump(self):
        return dissoc(self.__dict__, '_sa_instance_state')

    def to_dict(self, decode_json=True):
        data_dict = self.dump()
        if isinstance(data_dict.get('json_metadata'), str) and decode_json:
            data_dict['json_metadata'] = sbds.sbds_json.loads(
                data_dict['json_metadata'])
        return data_dict

    def to_json(self):
        data_dict = self.to_dict()
        return sbds.sbds_json.dumps(data_dict)

    def __repr__(self):
        return "<%s (block_num:%s transaction_num: %s operation_num: %s keys: %s)>" % (
            self.__class__.__name__, self.block_num, self.transaction_num,
            self.operation_num, tuple(self.dump().keys()))

    def __str__(self):
        return str(self.dump())
