
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

class AuthorRewardOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct author_reward_operation : public virtual_operation {
      author_reward_operation(){}
      author_reward_operation( const account_name_type& a, const string& p, const asset& s, const asset& st, const asset& v )
         :author(a), permlink(p), sbd_payout(s), steem_payout(st), vesting_payout(v){}

      account_name_type author;
      string            permlink;
      asset             sbd_payout;
      asset             steem_payout;
      asset             vesting_payout;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_author_reward_operations'
    __operation_type__ = 'author_reward_operation'
    
    author = Column(Unicode(50))
    permlink = Column(Unicode(150))
    sbd_payout = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    steem_payout = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    vesting_payout = Column(Numeric(15, 6), nullable=False)
    # asset_symbol = Column(Unicode(5))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        sbd_payout=lambda x: amount_field(x.get('sbd_payout'), num_func=float),
        steem_payout=lambda x: amount_field(x.get('steem_payout'), num_func=float),
        vesting_payout=lambda x: amount_field(x.get('vesting_payout'), num_func=float),
    )

