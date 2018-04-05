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

from ...import Base
from ....enums import operation_types_enum
from ....field_handlers import json_string_field
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field


class ProducerRewardVirtualOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_producer_rewards'
    __table_args__ = (


        ForeignKeyConstraint(['producer'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_virtual_producer_rewards_accounts', 'accounts', postgresql_using='gin')

    )

    id = Column(Integer, primary_key=True)

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(ARRAY(String(16)))
    producer = Column(String(16), nullable=True)  # steem_type:account_name_type
    vesting_shares = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    vesting_shares_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(operation_types_enum, nullable=False, default='producer_reward')

    _fields = dict(
        vesting_shares=lambda x: amount_field(
            x.get('vesting_shares'), num_func=float),  # steem_type:asset
        vesting_shares_symbol=lambda x: amount_symbol_field(
            x.get('vesting_shares')),  # steem_type:asset
        accounts=lambda x: tuple(flatten((x.get('producer'),)))
    )

    _account_fields = frozenset(['producer', ])
