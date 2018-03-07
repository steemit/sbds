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


class AuthorRewardVirtualOperation(Base, BaseVirtualOperation):
    """


    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_author_rewards'
    __operation_type__ = 'author_reward_operation'

    # steem_type:account_name_type
    author = Column(String(50), ForeignKey("sbds_meta_accounts.name"))
    permlink = Column(Unicode(256), index=True)  # name:permlink
    sbd_payout = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    sbd_payout_symbol = Column(String(5))  # steem_type:asset
    steem_payout = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    steem_payout_symbol = Column(String(5))  # steem_type:asset
    vesting_payout = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    vesting_payout_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='author_reward_operation')

    _fields = dict(
        sbd_payout=lambda x: amount_field(x.get('sbd_payout'), num_func=float),
        sbd_payout_symbol=lambda x: amount_symbol_field(x.get('sbd_payout')),
        steem_payout=lambda x: amount_field(x.get('steem_payout'), num_func=float),
        steem_payout_symbol=lambda x: amount_symbol_field(x.get('steem_payout')),
        vesting_payout=lambda x: amount_field(x.get('vesting_payout'), num_func=float),
        vesting_payout_symbol=lambda x: amount_symbol_field(x.get('vesting_payout')),
    )
