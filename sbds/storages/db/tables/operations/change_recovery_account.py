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


class ChangeRecoveryAccountOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "new_recovery_account": "boombastic",
      "account_to_recover": "barrie",
      "extensions": []
    }



    """

    __tablename__ = 'sbds_op_change_recovery_accounts'
    __operation_type__ = 'change_recovery_account_operation'

    account_to_recover = Column(String(50), ForeignKey(
        "sbds_meta_accounts.name"))  # steem_type:account_name_type
    new_recovery_account = Column(String(50), ForeignKey(
        "sbds_meta_accounts.name"))  # steem_type:account_name_type
    extensions = Column(JSONB)  # steem_type:extensions_type
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='change_recovery_account_operation')

    _fields = dict(

    )
