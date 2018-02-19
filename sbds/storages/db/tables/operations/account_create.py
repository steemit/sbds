# coding=utf-8
import os.path

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

from sqlalchemy.dialects.mysql import JSON

from toolz import get_in

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class AccountCreateOperation(Base, BaseOperation):
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
    __operation_type__ = 'account_create_operation'
    
    fee = Column(Numeric(20,6), nullable=False) # steem_type:asset
    fee_symbol = Column(String(5)) # steem_type:asset
    creator = Column(String(50), index=True) # steem_type:account_name_type
    new_account_name = Column(String(50), index=True) # steem_type:account_name_type
    owner = Column(JSON) # name:owner
    active = Column(JSON) # name:active
    posting = Column(JSON) # name:posting
    memo_key = Column(String(60), nullable=False) # steem_type:public_key_type
    json_metadata = Column(JSON) # name:json_metadata
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='account_create_operation')
    
    _fields = dict(
        fee=lambda x: amount_field(x.get('fee'), num_func=float),
        fee_symbol=lambda x: amount_symbol_field(x.get('fee')),
        creator=lambda x: x.get('creator'),
        new_account_name=lambda x: x.get('new_account_name'),
        owner=lambda x: x.get('owner'),
        active=lambda x: x.get('active'),
        posting=lambda x: x.get('posting'),
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'),
    )

