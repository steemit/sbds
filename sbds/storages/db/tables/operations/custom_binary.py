
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

class CustomBinaryOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================

    

    """
    
    __tablename__ = 'sbds_op_custom_binaries'
    __operation_type__ = 'custom_binary_operation'
    
    required_owner_auths = Column(JSON) # steem_type:flat_set< account_name_type>
    required_active_auths = Column(JSON) # steem_type:flat_set< account_name_type>
    required_posting_auths = Column(JSON) # steem_type:flat_set< account_name_type>
    required_auths = Column(String(100)) # steem_type:vector< authority>
    id = Column(Unicode(150)) # steem_type:string
    data = Column(String(100)) # steem_type:vector< char>
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='custom_binary_operation')
    
    _fields = dict(
        required_owner_auths=lambda x: x.get('required_owner_auths'),
        required_active_auths=lambda x: x.get('required_active_auths'),
        required_posting_auths=lambda x: x.get('required_posting_auths'),
        required_auths=lambda x: x.get('required_auths'),
        id=lambda x: x.get('id'),
        data=lambda x: x.get('data'),
    )

