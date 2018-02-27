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


class EscrowApproveOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "who": "on0tole",
      "approve": true,
      "from": "xtar",
      "agent": "on0tole",
      "to": "testz",
      "escrow_id": 59102208
    }



    """

    __tablename__ = 'sbds_op_escrow_approves'
    __operation_type__ = 'escrow_approve_operation'

    _from = Column('from', String(50), ForeignKey('sbds_meta_accounts.name'))  # name:from
    to = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    agent = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    who = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    escrow_id = Column(Integer)  # steem_type:uint32_t
    approve = Column(Boolean)  # steem_type:bool
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='escrow_approve_operation')

    _fields = dict(

    )
