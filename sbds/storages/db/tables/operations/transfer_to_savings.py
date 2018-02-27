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


class TransferToSavingsOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "from": "abit",
      "to": "abit",
      "amount": "1.000 SBD",
      "memo": ""
    }



    """

    __tablename__ = 'sbds_op_transfer_to_saving'
    __operation_type__ = 'transfer_to_savings_operation'

    _from = Column('from', String(50), ForeignKey('sbds_meta_accounts.name'))  # name:from
    to = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    amount = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    amount_symbol = Column(String(5))  # steem_type:asset
    memo = Column(UnicodeText)  # name:memo
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='transfer_to_savings_operation')

    _fields = dict(
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x.get('amount')),
    )
