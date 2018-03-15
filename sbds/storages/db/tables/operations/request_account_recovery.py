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
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),
        ForeignKeyConstraint(['recovery_account'], ['sbds_meta_accounts.name'],
            deferrable=True, initially='DEFERRED', use_alter=True),
        ForeignKeyConstraint(['account_to_recover'], ['sbds_meta_accounts.name'],
            deferrable=True, initially='DEFERRED', use_alter=True),)

    
    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False, index=True)
    operation_num = Column(SmallInteger, nullable=False, index=True)
    trx_id = Column(String(40),nullable=False)
    timestamp = Column(DateTime(timezone=False))
    recovery_account = Column(String(16)) # steem_type:account_name_type
    account_to_recover = Column(String(16)) # steem_type:account_name_type
    new_owner_authority = Column(JSONB) # steem_type:authority
    extensions = Column(JSONB) # steem_type:extensions_type
    operation_type = Column(operation_types_enum,nullable=False,index=True,default='request_account_recovery')


    _fields = dict(
        new_owner_authority=lambda x:json_string_field(x.get('new_owner_authority')), # steem_type:authority
        extensions=lambda x:json_string_field(x.get('extensions')), # steem_type:extensions_type
        
    )

    _account_fields = frozenset(['recovery_account','account_to_recover',])

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
