# -*- coding: utf-8 -*-

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
from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import JSONB

from ...import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field
from ..base import BaseOperation
from ..base import BaseVirtualOperation


class LiquidityRewardVirtualOperation(Base, BaseVirtualOperation):
    """


    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_liquidity_rewards'
    __operation_type__ = 'liquidity_reward_operation'

    owner = Column(JSONB)  # name:owner
    payout = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    payout_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='liquidity_reward_operation')

    _fields = dict(
        payout=lambda x: amount_field(x.get('payout'), num_func=float),
        payout_symbol=lambda x: amount_symbol_field(x.get('payout')),
    )
