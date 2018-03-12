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

class AccountUpdateOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "json_metadata": "",
      "account": "theoretical",
      "memo_key": "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
      "posting": {
        "key_auths": [
          [
            "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
            1
          ],
          [
            "STM76EQNV2RTA6yF9TnBvGSV71mW7eW36MM7XQp24JxdoArTfKA76",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      }
    }



    """

    __tablename__ = 'sbds_op_account_updates'
    __operation_type__ = 'account_update_operation'

    account = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    owner = Column(JSONB) # steem_type:optional< authority>
    active = Column(JSONB) # steem_type:optional< authority>
    posting = Column(JSONB) # steem_type:optional< authority>
    memo_key = Column(String(60), nullable=False) # steem_type:public_key_type
    json_metadata = Column(JSONB) # name:json_metadata
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='account_update')

    _fields = dict(
        owner=lambda x:json_string_field(x.get('owner')), # steem_type:optional< authority>
        active=lambda x: json_string_field(x.get('active')), # name:active
        posting=lambda x: json_string_field(x.get('posting')), # name:posting
        json_metadata=lambda x: json_string_field(x.get('json_metadata')), # name:json_metadata
    )


