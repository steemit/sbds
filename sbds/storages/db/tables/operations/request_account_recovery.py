# -*- coding: utf-8 -*-

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

    recovery_account = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    account_to_recover = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    new_owner_authority = Column(JSONB)  # steem_type:authority
    extensions = Column(JSONB)  # steem_type:extensions_type
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='request_account_recovery_operation')

    _fields = dict(

    )
