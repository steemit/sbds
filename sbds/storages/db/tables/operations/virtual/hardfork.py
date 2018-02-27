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


class HardforkVirtualOperation(Base, BaseVirtualOperation):
    """


    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_hardforks'
    __operation_type__ = 'hardfork_operation'

    hardfork_id = Column(Integer)  # steem_type:uint32_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='hardfork_operation')

    _fields = dict(

    )
