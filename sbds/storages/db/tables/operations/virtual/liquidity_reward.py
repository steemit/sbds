# -*- coding: utf-8 -*-

import dateutil.parser
import rapidjson

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
from ....field_handlers import json_string_field
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

    owner = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    payout = Column(Numeric(20,6), nullable=False) # steem_type:asset
    payout_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='liquidity_reward')

    _fields = dict(
        payout=lambda x: amount_field(x.get('payout'), num_func=float), # steem_type:asset
        payout_symbol=lambda x: amount_symbol_field(x.get('payout')), # steem_type:asset
    )


