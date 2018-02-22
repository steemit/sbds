# coding=utf-8

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

#from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import JSON

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
    
    reset_account = Column(String(50), index=True) # steem_type:account_name_type
    account_to_reset = Column(String(50), index=True) # steem_type:account_name_type
    new_owner_authority = Column(JSON) # steem_type:authority
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='reset_account_operation')
    
    _fields = dict(
        reset_account=lambda x: x.get('reset_account'),
        account_to_reset=lambda x: x.get('account_to_reset'),
        new_owner_authority=lambda x: x.get('new_owner_authority'),
    )


