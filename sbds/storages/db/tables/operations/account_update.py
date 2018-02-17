
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
    
    account = Column(String(50), index=True) # steem_type:account_name_type
    owner = Column(JSON) # name:owner
    active = Column(JSON) # name:active
    posting = Column(JSON) # name:posting
    memo_key = Column(String(80), nullable=False) # steem_type:public_key_type
    json_metadata = Column(JSON) # name:json_metadata
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='account_update_operation')
    
    _fields = dict(
        account=lambda x: x.get('account'),
        owner=lambda x: x.get('owner'),
        active=lambda x: x.get('active'),
        posting=lambda x: x.get('posting'),
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'),
    )

