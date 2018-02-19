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

class RequestAccountRecoveryOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "new_owner_authority": {
        "key_auths": [
          [
            "STM6LYxj96zdypHYqgDdD6Nyh2NxerN3P1Mp3ddNm7gci63nfrSuZ",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      },
      "account_to_recover": "gandalf",
      "recovery_account": "steem",
      "extensions": []
    }

    

    """
    
    __tablename__ = 'sbds_op_request_account_recoveries'
    __operation_type__ = 'request_account_recovery_operation'
    
    recovery_account = Column(String(50), index=True) # steem_type:account_name_type
    account_to_recover = Column(String(50), index=True) # steem_type:account_name_type
    new_owner_authority = Column(JSON) # steem_type:authority
    extensions = Column(JSON) # steem_type:extensions_type
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='request_account_recovery_operation')
    
    _fields = dict(
        recovery_account=lambda x: x.get('recovery_account'),
        account_to_recover=lambda x: x.get('account_to_recover'),
        new_owner_authority=lambda x: x.get('new_owner_authority'),
        extensions=lambda x: x.get('extensions'),
    )

