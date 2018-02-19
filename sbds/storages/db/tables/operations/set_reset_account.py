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

class SetResetAccountOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_set_reset_accounts'
    __operation_type__ = 'set_reset_account_operation'
    
    account = Column(String(50), index=True) # steem_type:account_name_type
    current_reset_account = Column(String(50), index=True) # steem_type:account_name_type
    reset_account = Column(String(50), index=True) # steem_type:account_name_type
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='set_reset_account_operation')
    
    _fields = dict(
        account=lambda x: x.get('account'),
        current_reset_account=lambda x: x.get('current_reset_account'),
        reset_account=lambda x: x.get('reset_account'),
    )

