# coding=utf-8

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

#from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import JSON

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class AccountCreateWithDelegationOperation(Base, BaseOperation):
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
    __operation_type__ = 'account_create_with_delegation_operation'
    
    fee = Column(Numeric(20,6), nullable=False) # steem_type:asset
    fee_symbol = Column(String(5)) # steem_type:asset
    delegation = Column(Numeric(20,6), nullable=False) # steem_type:asset
    delegation_symbol = Column(String(5)) # steem_type:asset
    creator = Column(String(50), index=True) # steem_type:account_name_type
    new_account_name = Column(String(50), index=True) # steem_type:account_name_type
    owner = Column(JSONB) # name:owner
    active = Column(JSONB) # name:active
    posting = Column(JSONB) # name:posting
    memo_key = Column(String(60), nullable=False) # steem_type:public_key_type
    json_metadata = Column(JSONB) # name:json_metadata
    extensions = Column(JSON) # steem_type:extensions_type
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='account_create_with_delegation_operation')
    
    _fields = dict(
        fee=lambda x: amount_field(x.get('fee'), num_func=float),
        fee_symbol=lambda x: amount_symbol_field(x.get('fee')),
        delegation=lambda x: amount_field(x.get('delegation'), num_func=float),
        delegation_symbol=lambda x: amount_symbol_field(x.get('delegation')),
        creator=lambda x: x.get('creator'),
        new_account_name=lambda x: x.get('new_account_name'),
        owner=lambda x: x.get('owner'),
        active=lambda x: x.get('active'),
        posting=lambda x: x.get('posting'),
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'),
        extensions=lambda x: x.get('extensions'),
    )


