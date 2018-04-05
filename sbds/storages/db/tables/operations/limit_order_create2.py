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


class LimitOrderCreate2Operation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_limit_order_create2s'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['owner'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_limit_order_create2s_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(ARRAY(String(16)))
    owner = Column(String(16), nullable=True)  # steem_type:account_name_type
    orderid = Column(Numeric)  # steem_type:uint32_t
    amount_to_sell = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    amount_to_sell_symbol = Column(String(5))  # steem_type:asset
    fill_or_kill = Column(Boolean)  # steem_type:bool
    exchange_rate = Column(JSONB)  # steem_type:price
    expiration = Column(DateTime)  # steem_type:time_point_sec
    operation_type = Column(operation_types_enum, nullable=False, default='limit_order_create2')

    _fields = dict(
        amount_to_sell=lambda x: amount_field(
            x.get('amount_to_sell'), num_func=float),  # steem_type:asset
        amount_to_sell_symbol=lambda x: amount_symbol_field(
            x.get('amount_to_sell')),  # steem_type:asset
        exchange_rate=lambda x: json_string_field(x.get('exchange_rate')),  # steem_type:price
        expiration=lambda x: dateutil.parser.parse(
            x.get('expiration')),  # steem_type:time_point_sec
        accounts=lambda x: tuple(flatten((x.get('owner'),)))
    )

    _account_fields = frozenset(['owner', ])
