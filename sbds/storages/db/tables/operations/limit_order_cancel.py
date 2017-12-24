# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, BigInteger, Enum

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class LimitOrderCancelOperation(Base, BaseOperation):
    """

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_limit_order_cancels'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    owner = Column(Unicode(50), nullable=False)
    orderid = Column(BigInteger, nullable=False)

    _fields = dict(
        owner=lambda x: x.get('owner'), orderid=lambda x: x.get('orderid')
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

