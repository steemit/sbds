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

class EquihashPow(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================


    

    """
    
    __tablename__ = 'sbds_op_equihash_pows'
    __operation_type__ = 'equihash_pow'
    
    input = Column(JSON) # steem_type:pow2_input
    proof = Column(JSON) # steem_type:fc::equihash::proof
    prev_block = Column(Integer) # steem_type:block_id_type
    pow_summary = Column(Integer) # steem_type:uint32_t
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='equihash_pow')
    
    _fields = dict(
        input=lambda x: x.get('input'),
        proof=lambda x: x.get('proof'),
        prev_block=lambda x: x.get('prev_block'),
        pow_summary=lambda x: x.get('pow_summary'),
    )

