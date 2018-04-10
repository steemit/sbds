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


class FeedPublishOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "exchange_rate": {
        "quote": "1000.000 STEEM",
        "base": "1.000 SBD"
      },
      "publisher": "abit"
    }



    """

    __tablename__ = 'sbds_op_feed_publishes'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['publisher'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_feed_publishes_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    publisher = Column(String(16), nullable=True)  # steem_type:account_name_type
    exchange_rate = Column(JSONB)  # steem_type:price
    operation_type = Column(operation_types_enum, nullable=False, default='feed_publish')

    _fields = dict(
        exchange_rate=lambda x: json_string_field(x.get('exchange_rate')),  # steem_type:price
        accounts=lambda x: sbds.sbds_json.dumps(
            [acct for acct in set(flatten((x.get('publisher'),))) if acct])
    )

    _account_fields = frozenset(['publisher', ])
