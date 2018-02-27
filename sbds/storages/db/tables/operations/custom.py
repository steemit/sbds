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


class CustomOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "id": 0,
      "data": "276e1c988628df33",
      "required_auths": [
        "blocktrades"
      ]
    }



    """

    __tablename__ = 'sbds_op_customs'
    __operation_type__ = 'custom_operation'

    required_auths = Column(JSONB)  # steem_type:flat_set< account_name_type>
    id = Column(SmallInteger)  # steem_type:uint16_t
    data = Column(String(100))  # steem_type:vector< char>
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='custom_operation')

    _fields = dict(

    )
