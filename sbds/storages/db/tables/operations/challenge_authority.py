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

class ChallengeAuthorityOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_challenge_authorities'
    __operation_type__ = 'challenge_authority_operation'
    
    challenger = Column(String(50), index=True) # steem_type:account_name_type
    challenged = Column(String(50), index=True) # steem_type:account_name_type
    require_owner = Column(Boolean) # steem_type:bool
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='challenge_authority_operation')
    
    _fields = dict(
        challenger=lambda x: x.get('challenger'),
        challenged=lambda x: x.get('challenged'),
        require_owner=lambda x: x.get('require_owner'),
    )

