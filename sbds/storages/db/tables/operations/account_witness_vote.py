
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

class AccountWitnessVoteOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "account": "donalddrumpf",
      "approve": true,
      "witness": "berniesanders"
    }
    

    """
    
    __tablename__ = 'sbds_op_account_witness_votes'
    __operation_type__ = 'account_witness_vote_operation'
    
    account = Column(String(50), index=True) # steem_type:account_name_type
    witness = Column(String(50), index=True) # steem_type:account_name_type
    approve = Column(Boolean) # steem_type:bool
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='account_witness_vote_operation')
    
    _fields = dict(
        account=lambda x: x.get('account'),
        witness=lambda x: x.get('witness'),
        approve=lambda x: x.get('approve'),
    )

