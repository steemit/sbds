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


class WitnessUpdateOperation(Base, BaseOperation):
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
    __operation_type__ = 'witness_update_operation'

    owner = Column(JSONB)  # name:owner
    url = Column(Unicode(150))  # steem_type:string
    block_signing_key = Column(String(60), nullable=False)  # steem_type:public_key_type
    props = Column(JSONB)  # steem_type:chain_properties
    fee = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    fee_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='witness_update_operation')

    _fields = dict(
        fee=lambda x: amount_field(x.get('fee'), num_func=float),
        fee_symbol=lambda x: amount_symbol_field(x.get('fee')),
    )
