
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

class CommentBenefactorRewardOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================

    

    """
    
    __tablename__ = 'sbds_op_comment_benefactor_rewards'
    __operation_type__ = 'comment_benefactor_reward_operation'
    
    benefactor = Column(String(50), index=True) # steem_type:account_name_type
    author = Column(String(50), index=True) # steem_type:account_name_type
    permlink = Column(Unicode(150)) # steem_type:string
    reward = Column(Numeric(15,6), nullable=False) # steem_type:asset
    reward_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='comment_benefactor_reward_operation')
    
    _fields = dict(
        benefactor=lambda x: x.get('benefactor'),
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        reward=lambda x: amount_field(x.get('reward'), num_func=float),
        reward_symbol=lambda x: amount_symbol_field(x.get('reward')),
    )

