
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

class ReturnVestingDelegationOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================

    

    """
    
    __tablename__ = 'sbds_op_return_vesting_delegations'
    __operation_type__ = 'return_vesting_delegation_operation'
    
    account = Column(String(50), index=True) # steem_type:account_name_type
    vesting_shares = Column(Numeric(15,6), nullable=False) # steem_type:asset
    vesting_shares_symbol = Column(String(5)) # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='return_vesting_delegation_operation')
    
    _fields = dict(
        account=lambda x: x.get('account'),
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float),
        vesting_shares_symbol=lambda x: amount_symbol_field(x.get('vesting_shares')),
    )

