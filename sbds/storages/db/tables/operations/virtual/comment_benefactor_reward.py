
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

class CommentBenefactorRewardOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct comment_benefactor_reward_operation : public virtual_operation
   {
      comment_benefactor_reward_operation() {}
      comment_benefactor_reward_operation( const account_name_type& b, const account_name_type& a, const string& p, const asset& r )
         : benefactor( b ), author( a ), permlink( p ), reward( r ) {}

      account_name_type benefactor;
      account_name_type author;
      string            permlink;
      asset             reward;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_comment_benefactor_reward_operations'
    __operation_type__ = 'comment_benefactor_reward_operation'
    
    benefactor = Column(Unicode(50))
    author = Column(Unicode(50))
    permlink = Column(Unicode(150))
    reward = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        benefactor=lambda x: x.get('benefactor'),
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        reward=lambda x: amount_field(x.get('reward'), num_func=float),
    )

