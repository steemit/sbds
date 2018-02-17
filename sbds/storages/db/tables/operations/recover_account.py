
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

class RecoverAccountOperation(Base, BaseOperation):
    """
    
    
    Steem Blockchain Example
    ======================
    {
      "new_owner_authority": {
        "key_auths": [
          [
            "STM7j3nhkhHTpXqLEvdx2yEGhQeeorTcxSV6WDL2DZGxwUxYGrHvh",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      },
      "recent_owner_authority": {
        "key_auths": [
          [
            "STM78Xth94gNxp8nmByFV2vNAhg9bsSdviJ6fQXUTFikySLK3uTxC",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      },
      "account_to_recover": "chitty",
      "extensions": []
    }
    

    """
    
    __tablename__ = 'sbds_op_recover_accounts'
    __operation_type__ = 'recover_account_operation'
    
    account_to_recover = Column(String(50), index=True) # steem_type:account_name_type
    new_owner_authority = Column(JSON) # steem_type:authority
    recent_owner_authority = Column(JSON) # steem_type:authority
    extensions = Column(JSON) # steem_type:extensions_type
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='recover_account_operation')
    
    _fields = dict(
        account_to_recover=lambda x: x.get('account_to_recover'),
        new_owner_authority=lambda x: x.get('new_owner_authority'),
        recent_owner_authority=lambda x: x.get('recent_owner_authority'),
        extensions=lambda x: x.get('extensions'),
    )

