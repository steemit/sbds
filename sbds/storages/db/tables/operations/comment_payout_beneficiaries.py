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

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class CommentPayoutBeneficiaries(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_comment_payout_beneficiary'
    __operation_type__ = 'comment_payout_beneficiaries'
    
    beneficiaries = Column(JSON) # steem_type:vector< beneficiary_route_type>
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='comment_payout_beneficiaries')
    
    _fields = dict(
        beneficiaries=lambda x: x.get('beneficiaries'),
    )

