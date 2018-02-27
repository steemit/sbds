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


class DelegateVestingSharesOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "vesting_shares": "94599167.138276 VESTS",
      "delegator": "liberosist",
      "delegatee": "dunia"
    }



    """

    __tablename__ = 'sbds_op_delegate_vesting_share'
    __operation_type__ = 'delegate_vesting_shares_operation'

    delegator = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    delegatee = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    vesting_shares = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    vesting_shares_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='delegate_vesting_shares_operation')

    _fields = dict(
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float),
        vesting_shares_symbol=lambda x: amount_symbol_field(x.get('vesting_shares')),
    )
