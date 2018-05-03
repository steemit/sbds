# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field
from ...field_handlers import json_string_field


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
    __table_args__ = (ForeignKeyConstraint(
        ['publisher'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        UniqueConstraint('block_num', 'transaction_num',
                         'operation_num', 'raw'),
        Index(
        'ix_sbds_op_feed_publishes_accounts',
        'accounts',
        postgresql_using='gin',
        postgresql_ops={'accounts': 'jsonb_path_ops'}))

    _id = Column(BigInteger, autoincrement=True, primary_key=True)
    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(Text, nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    publisher = Column(Text, nullable=True)  # steem_type:account_name_type
    exchange_rate = Column(JSONB)  # steem_type:price
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        exchange_rate=lambda x: json_string_field(x.get('exchange_rate')),  # steem_type:price
        accounts=lambda x: accounts_field(x, 'feed_publish'),
    )

    _account_fields = frozenset([
        'publisher',
    ])
