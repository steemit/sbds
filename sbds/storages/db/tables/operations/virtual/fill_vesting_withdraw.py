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


class FillVestingWithdrawVirtualOperation(Base, BaseVirtualOperation):
    """


    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_fill_vesting_withdraws'
    __operation_type__ = 'fill_vesting_withdraw_operation'

    from_account = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    to_account = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    withdrawn = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    withdrawn_symbol = Column(String(5))  # steem_type:asset
    deposited = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    deposited_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='fill_vesting_withdraw_operation')

    _fields = dict(
        withdrawn=lambda x: amount_field(x.get('withdrawn'), num_func=float),
        withdrawn_symbol=lambda x: amount_symbol_field(x.get('withdrawn')),
        deposited=lambda x: amount_field(x.get('deposited'), num_func=float),
        deposited_symbol=lambda x: amount_symbol_field(x.get('deposited')),
    )
