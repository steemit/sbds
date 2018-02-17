
# coding=utf-8
import os.path

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

from sqlalchemy.dialects.mysql import JSON

from toolz import get_in

from ... import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field
from ..base import BaseOperation

class BeneficiaryRouteType(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================

    

    """
    
    __tablename__ = 'sbds_op_beneficiary_route_types'
    __operation_type__ = 'beneficiary_route_type'
    
    account = Column(String(50), index=True) # steem_type:account_name_type
    weight = Column(SmallInteger) # steem_type:uint16_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='beneficiary_route_type')
    
    _fields = dict(
        account=lambda x: x.get('account'),
        weight=lambda x: x.get('weight'),
    )

