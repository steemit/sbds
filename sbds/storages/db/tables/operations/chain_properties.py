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

class ChainProperties(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_chain_property'
    __operation_type__ = 'chain_properties'
    
    account_creation_fee = Column(Numeric(20,6), nullable=False) # steem_type:asset
    account_creation_fee_symbol = Column(String(5)) # steem_type:asset
    maximum_block_size = Column(Integer) # steem_type:uint32_t
    sbd_interest_rate = Column(SmallInteger) # steem_type:uint16_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='chain_properties')
    
    _fields = dict(
        account_creation_fee=lambda x: amount_field(x.get('account_creation_fee'), num_func=float),
        account_creation_fee_symbol=lambda x: amount_symbol_field(x.get('account_creation_fee')),
        maximum_block_size=lambda x: x.get('maximum_block_size'),
        sbd_interest_rate=lambda x: x.get('sbd_interest_rate'),
    )

