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


class LimitOrderCancelOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "orderid": 10,
      "owner": "linouxis9"
    }



    """

    __tablename__ = 'sbds_op_limit_order_cancels'
    __operation_type__ = 'limit_order_cancel_operation'

    owner = Column(JSONB)  # name:owner
    orderid = Column(Integer)  # steem_type:uint32_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='limit_order_cancel_operation')

    _fields = dict(

    )
