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
from sqlalchemy import ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from toolz.dicttoolz import dissoc

import sbds.sbds_json

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field


class Pow2Operation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "props": {
        "sbd_interest_rate": 1000,
        "account_creation_fee": "0.001 STEEM",
        "maximum_block_size": 131072
      },
      "work": [
        0,
        {
          "pow_summary": 3817904373,
          "input": {
            "worker_account": "aizen06",
            "nonce": "1052853013628665497",
            "prev_block": "003ea604345523c344fbadab605073ea712dd76f"
          }
        }
      ]
    }



    """

    __tablename__ = 'sbds_op_pow2s'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),
    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(ARRAY(String(16)))
    work = Column(JSONB)  # steem_type:steemit::protocol::pow2_work
    new_owner_key = Column(String(60))  # steem_type:optional< public_key_type>
    props = Column(JSONB)  # steem_type:chain_properties
    operation_type = Column(operation_types_enum, nullable=False, default='pow2')

    _fields = dict(
        work=lambda x: json_string_field(x.get('work')),  # steem_type:steemit::protocol::pow2_work
        props=lambda x: json_string_field(x.get('props')),  # steem_type:chain_properties
    )

    _account_fields = frozenset([])
