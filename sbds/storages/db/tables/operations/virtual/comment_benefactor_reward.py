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
from sqlalchemy.dialects.postgresql import JSONB

import sbds.sbds_json

from ...import Base
from ....enums import operation_types_enum
from ....field_handlers import json_string_field
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field


class CommentBenefactorRewardVirtualOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_comment_benefactor_rewards'
    __table_args__ = (


        ForeignKeyConstraint(['benefactor'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),



        ForeignKeyConstraint(['author'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index(
            'ix_sbds_op_virtual_comment_benefactor_rewards_accounts',
            'accounts',
            postgresql_using='gin')

    )

    id = Column(Integer, primary_key=True)

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    benefactor = Column(String(16), nullable=True)  # steem_type:account_name_type
    author = Column(String(16), nullable=True)  # steem_type:account_name_type
    permlink = Column(Unicode(256), index=True)  # name:permlink
    reward = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    reward_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        default='comment_benefactor_reward')

    _fields = dict(
        reward=lambda x: amount_field(x.get('reward'), num_func=float),  # steem_type:asset
        reward_symbol=lambda x: amount_symbol_field(x.get('reward')),  # steem_type:asset
        accounts=lambda x: sbds.sbds_json.dumps([acct for acct in set(
            flatten((x.get('benefactor'), x.get('author'),))) if acct])
    )

    _account_fields = frozenset(['benefactor', 'author', ])
