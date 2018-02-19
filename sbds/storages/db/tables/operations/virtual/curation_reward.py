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

from ...import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field
from ..base import BaseOperation
from ..base import BaseVirtualOperation

class CurationRewardOperation(Base, BaseVirtualOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_curation_rewards'
    __operation_type__ = 'curation_reward_operation'
    
    curator = Column(String(50), index=True) # steem_type:account_name_type
    reward = Column(Numeric(20,6), nullable=False) # steem_type:asset
    reward_symbol = Column(String(5)) # steem_type:asset
    comment_author = Column(String(50), index=True) # steem_type:account_name_type
    comment_permlink = Column(Unicode(150)) # steem_type:string
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='curation_reward_operation')
    
    _fields = dict(
        curator=lambda x: x.get('curator'),
        reward=lambda x: amount_field(x.get('reward'), num_func=float),
        reward_symbol=lambda x: amount_symbol_field(x.get('reward')),
        comment_author=lambda x: x.get('comment_author'),
        comment_permlink=lambda x: x.get('comment_permlink'),
    )

