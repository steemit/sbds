
# coding=utf-8
import os.path

from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from toolz import get_in

from ... import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ..base import BaseOperation

class CurationRewardOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct curation_reward_operation : public virtual_operation
   {
      curation_reward_operation(){}
      curation_reward_operation( const string& c, const asset& r, const string& a, const string& p )
         :curator(c), reward(r), comment_author(a), comment_permlink(p) {}

      account_name_type curator;
      asset             reward;
      account_name_type comment_author;
      string            comment_permlink;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_curation_reward_operations'
    __operation_type__ = 'curation_reward_operation'
    
    curator = Column(Unicode(50))
    reward = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    comment_author = Column(Unicode(50))
    comment_permlink = Column(Unicode(150))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        curator=lambda x: x.get('curator'),
        reward=lambda x: amount_field(x.get('reward'), num_func=float),
        comment_author=lambda x: x.get('comment_author'),
        comment_permlink=lambda x: x.get('comment_permlink'),
    )

