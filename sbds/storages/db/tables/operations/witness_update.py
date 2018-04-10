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


class WitnessUpdateOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "fee": "0.000 STEEM",
      "url": "fmooo/steemd-docker",
      "props": {
        "sbd_interest_rate": 1000,
        "account_creation_fee": "100.000 STEEM",
        "maximum_block_size": 131072
      },
      "owner": "steempty",
      "block_signing_key": "STM8LoQjQqJHvotqBo7HjnqmUbFW9oJ2theyqonzUd9DdJ7YYHsvD"
    }



    """

    __tablename__ = 'sbds_op_witness_updates'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['owner'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_witness_updates_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    owner = Column(String(16), nullable=True)  # steem_type:account_name_type
    url = Column(UnicodeText)  # steem_type:string -> default
    block_signing_key = Column(String(60), nullable=False)  # steem_type:public_key_type
    props = Column(JSONB)  # steem_type:chain_properties
    fee = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    fee_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(operation_types_enum, nullable=False, default='witness_update')

    _fields = dict(
        props=lambda x: json_string_field(x.get('props')),  # steem_type:chain_properties
        fee=lambda x: amount_field(x.get('fee'), num_func=float),  # steem_type:asset
        fee_symbol=lambda x: amount_symbol_field(x.get('fee')),  # steem_type:asset
        accounts=lambda x: sbds.sbds_json.dumps(
            [acct for acct in set(flatten((x.get('owner'),))) if acct])
    )

    _account_fields = frozenset(['owner', ])
