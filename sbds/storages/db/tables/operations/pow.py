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


class PowOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "worker_account": "admin",
      "nonce": 82,
      "block_id": "000004433bd4602cf5f74dbb564183837df9cef8",
      "props": {
        "sbd_interest_rate": 1000,
        "account_creation_fee": "100.000 STEEM",
        "maximum_block_size": 131072
      },
      "work": {
        "signature": "1f3f83209097efcd01b7d6f27ce726164323d503d6fcf4d55bfb7cb3032796f6766738b36062b5850d69447fdf9c091cbc70825df5eeacc4710a0b11ffdbf0912a",
        "input": "59b009f89477919f95914151cef06f28bf344dd6fb7670aca1c1f4323c80446b",
        "worker": "STM65wH1LZ7BfSHcK69SShnqCAH5xdoSZpGkUjmzHJ5GCuxEK9V5G",
        "work": "0b62f4837801cd857f01d6a541faeb13d6bb95f1c36c6b4b14a47df632aa6c92"
      }
    }

    """

    __tablename__ = 'sbds_op_pows'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),
        ForeignKeyConstraint(['worker_account'], ['sbds_meta_accounts.name'],
            deferrable=True, initially='DEFERRED', use_alter=True),)

    
    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False, index=True)
    operation_num = Column(SmallInteger, nullable=False, index=True)
    trx_id = Column(String(40),nullable=False)
    timestamp = Column(DateTime(timezone=False))
    worker_account = Column(String(16)) # steem_type:account_name_type
    block_id = Column(String(40)) # steem_type:block_id_type
    nonce = Column(Numeric) # steem_type:uint64_t
    work = Column(JSONB) # steem_type:pow
    props = Column(JSONB) # steem_type:chain_properties
    operation_type = Column(operation_types_enum,nullable=False,index=True,default='pow')


    _fields = dict(
        work=lambda x:json_string_field(x.get('work')), # steem_type:pow
        props=lambda x:json_string_field(x.get('props')), # steem_type:chain_properties
        
    )

    _account_fields = frozenset(['worker_account',])

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
