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

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation


class CommentOptionsOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "allow_curation_rewards": true,
      "allow_votes": true,
      "permlink": "testing6",
      "percent_steem_dollars": 5000,
      "max_accepted_payout": "1000.000 SBD",
      "author": "testing001",
      "extensions": []
    }



    """

    __tablename__ = 'sbds_op_comment_option'
    __operation_type__ = 'comment_options_operation'

    author = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    permlink = Column(Unicode(512), index=True)  # name:permlink
    max_accepted_payout = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    max_accepted_payout_symbol = Column(String(5))  # steem_type:asset
    percent_steem_dollars = Column(SmallInteger)  # steem_type:uint16_t
    allow_votes = Column(Boolean)  # steem_type:bool
    allow_curation_rewards = Column(Boolean)  # steem_type:bool
    extensions = Column(JSONB)  # steem_type:steemit::protocol::comment_options_extensions_type
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='comment_options_operation')

    _fields = dict(
        max_accepted_payout=lambda x: amount_field(x.get('max_accepted_payout'), num_func=float),
        max_accepted_payout_symbol=lambda x: amount_symbol_field(x.get('max_accepted_payout')),
    )
