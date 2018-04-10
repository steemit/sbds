# -*- coding: utf-8 -*-
import dateutil.parser

from funcy import flatten
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
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB

import sbds.sbds_json

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field


class RecoverAccountOperation(Base):
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
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['account_to_recover'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_recover_accounts_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    account_to_recover = Column(String(16), nullable=True)  # steem_type:account_name_type
    new_owner_authority = Column(JSONB)  # steem_type:authority
    recent_owner_authority = Column(JSONB)  # steem_type:authority
    extensions = Column(JSONB)  # steem_type:extensions_type
    operation_type = Column(operation_types_enum, nullable=False, default='recover_account')

    _fields = dict(
        new_owner_authority=lambda x: json_string_field(
            x.get('new_owner_authority')),  # steem_type:authority
        recent_owner_authority=lambda x: json_string_field(
            x.get('recent_owner_authority')),  # steem_type:authority
        extensions=lambda x: json_string_field(x.get('extensions')),  # steem_type:extensions_type
        accounts=lambda x: sbds.sbds_json.dumps(
            [acct for acct in set(flatten((x.get('account_to_recover'),))) if acct])
    )

    _account_fields = frozenset(['account_to_recover', ])
