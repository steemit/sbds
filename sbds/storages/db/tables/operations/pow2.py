# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field


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
    __table_args__ = (Index(
        'ix_sbds_sbds_op_pow2s_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True), )

    _id = Column(BigInteger, autoincrement=True, primary_key=True)
    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(Text, nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    work = Column(JSONB)  # steem_type:steemit::protocol::pow2_work
    new_owner_key = Column(Text)  # steem_type:optional< public_key_type>
    props = Column(JSONB)  # steem_type:chain_properties
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        work=lambda x: json_string_field(x.get('work')),  # steem_type:steemit::protocol::pow2_work
        props=lambda x: json_string_field(x.get('props')),  # steem_type:chain_properties
    )

    _account_fields = frozenset([])
