
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

class CommentRewardOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct comment_reward_operation : public virtual_operation
   {
      comment_reward_operation(){}
      comment_reward_operation( const account_name_type& a, const string& pl, const asset& p )
         :author(a), permlink(pl), payout(p){}

      account_name_type author;
      string            permlink;
      asset             payout;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_comment_reward_operations'
    __operation_type__ = 'comment_reward_operation'
    
    author = Column(Unicode(50))
    permlink = Column(Unicode(150))
    payout = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        payout=lambda x: amount_field(x.get('payout'), num_func=float),
    )

