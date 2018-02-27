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


class ResetAccountOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_reset_accounts'
    __operation_type__ = 'reset_account_operation'

    reset_account = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    account_to_reset = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    new_owner_authority = Column(JSONB)  # steem_type:authority
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='reset_account_operation')

    _fields = dict(

    )
