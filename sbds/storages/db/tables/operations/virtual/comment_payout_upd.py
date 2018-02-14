
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

class CommentPayoutUpdateOperation(Base, BaseOperation):
    """
    
    CPP Class Definition
    ======================
    
    struct comment_payout_update_operation : public virtual_operation
   {
      comment_payout_update_operation() {}
      comment_payout_update_operation( const account_name_type& a, const string& p ) : author( a ), permlink( p ) {}

      account_name_type author;
      string            permlink;
   };
    
    
    """
    
    __tablename__ = 'sbds_op_comment_payout_update_operations'
    __operation_type__ = 'comment_payout_update_operation'
    
    author = Column(Unicode(50))
    permlink = Column(Unicode(150))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
    
    _fields = dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
    )

