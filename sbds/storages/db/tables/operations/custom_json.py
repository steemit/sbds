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

class CustomJsonOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "required_auths": [],
      "id": "follow",
      "json": "{\"follower\":\"steemit\",\"following\":\"steem\",\"what\":[\"posts\"]}",
      "required_posting_auths": [
        "steemit"
      ]
    }



    """

    __tablename__ = 'sbds_op_custom_jsons'
    __operation_type__ = 'custom_json_operation'

    required_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    required_posting_auths = Column(JSONB) # steem_type:flat_set< account_name_type>
    id = Column(UnicodeText) # steem_type:string -> default
    json = Column(JSONB) # name:json
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='custom_json')

    _fields = dict(
        required_auths=lambda x:json_string_field(x.get('required_auths')), # steem_type:flat_set< account_name_type>
        required_posting_auths=lambda x:json_string_field(x.get('required_posting_auths')), # steem_type:flat_set< account_name_type>
        json=lambda x: json_string_field(x.get('json')), # name:json
    )


