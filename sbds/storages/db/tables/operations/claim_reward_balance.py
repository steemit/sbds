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


class ClaimRewardBalanceOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "reward_steem": "0.017 STEEM",
      "reward_vests": "185.025103 VESTS",
      "account": "ocrdu",
      "reward_sbd": "0.011 SBD"
    }

    """

    __tablename__ = 'sbds_op_claim_reward_balances'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),
        ForeignKeyConstraint(['account'], ['sbds_meta_accounts.name'],
            deferrable=True, initially='DEFERRED', use_alter=True),)

    
    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False, index=True)
    operation_num = Column(SmallInteger, nullable=False, index=True)
    trx_id = Column(String(40),nullable=False)
    timestamp = Column(DateTime(timezone=False))
    account = Column(String(16)) # steem_type:account_name_type
    reward_steem = Column(Numeric(20,6), nullable=False) # steem_type:asset
    reward_steem_symbol = Column(String(5)) # steem_type:asset
    reward_sbd = Column(Numeric(20,6), nullable=False) # steem_type:asset
    reward_sbd_symbol = Column(String(5)) # steem_type:asset
    reward_vests = Column(Numeric(20,6), nullable=False) # steem_type:asset
    reward_vests_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(operation_types_enum,nullable=False,index=True,default='claim_reward_balance')


    _fields = dict(
        reward_steem=lambda x: amount_field(x.get('reward_steem'), num_func=float), # steem_type:asset
        reward_steem_symbol=lambda x: amount_symbol_field(x.get('reward_steem')), # steem_type:asset
        reward_sbd=lambda x: amount_field(x.get('reward_sbd'), num_func=float), # steem_type:asset
        reward_sbd_symbol=lambda x: amount_symbol_field(x.get('reward_sbd')), # steem_type:asset
        reward_vests=lambda x: amount_field(x.get('reward_vests'), num_func=float), # steem_type:asset
        reward_vests_symbol=lambda x: amount_symbol_field(x.get('reward_vests')), # steem_type:asset
        
    )

    _account_fields = frozenset(['account',])

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
