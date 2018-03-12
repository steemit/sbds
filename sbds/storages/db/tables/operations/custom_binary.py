# -*- coding: utf-8 -*-

import dateutil.parser
import rapidjson

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
from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import JSONB

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class CustomBinaryOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_custom_binaries'
    __operation_type__ = 'custom_binary_operation'

    required_owner_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    required_active_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    required_posting_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    required_auths = Column(JSONB) # steem_type:vector< authority>
    id = Column(UnicodeText) # steem_type:string -> default
    data = Column(String(100)) # steem_type:vector< char>
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='custom_binary')

    _fields = dict(
        required_owner_auths=lambda x:json_string_field(x.get('required_owner_auths')), # steem_type:flat_set< account_name_type>
        required_active_auths=lambda x:json_string_field(x.get('required_active_auths')), # steem_type:flat_set< account_name_type>
        required_posting_auths=lambda x:json_string_field(x.get('required_posting_auths')), # steem_type:flat_set< account_name_type>
        required_auths=lambda x:json_string_field(x.get('required_auths')), # steem_type:vector< authority>
    )


