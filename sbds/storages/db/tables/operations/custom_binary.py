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


class CustomBinaryOperation(Base):
    """

    Steem Blockchain Example
    ======================
    

    """

    __tablename__ = 'sbds_op_custom_binaries'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),)

    
    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False, index=True)
    operation_num = Column(SmallInteger, nullable=False, index=True)
    trx_id = Column(String(40),nullable=False)
    timestamp = Column(DateTime(timezone=False))
    required_owner_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    required_active_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    required_posting_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    required_auths = Column(JSONB) # steem_type:vector< authority>
    id = Column(UnicodeText) # steem_type:string -> default
    data = Column(String(100)) # steem_type:vector< char>
    operation_type = Column(operation_types_enum,nullable=False,index=True,default='custom_binary')


    _fields = dict(
        required_owner_auths=lambda x:json_string_field(x.get('required_owner_auths')), # steem_type:flat_set< account_name_type>
        required_active_auths=lambda x:json_string_field(x.get('required_active_auths')), # steem_type:flat_set< account_name_type>
        required_posting_auths=lambda x:json_string_field(x.get('required_posting_auths')), # steem_type:flat_set< account_name_type>
        required_auths=lambda x:json_string_field(x.get('required_auths')), # steem_type:vector< authority>
        
    )

    _account_fields = frozenset([])

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
