# -*- coding: utf-8 -*-

import dateutil.parser
import rapidjson

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
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class EscrowTransferOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "agent": "fabien",
      "sbd_amount": "1.000 SBD",
      "json_meta": "{}",
      "steem_amount": "0.000 STEEM",
      "escrow_expiration": "2017-02-28T11:22:39",
      "fee": "0.100 SBD",
      "to": "james",
      "ratification_deadline": "2017-02-26T11:22:39",
      "escrow_id": 23456789,
      "from": "siol"
    }



    """

    __tablename__ = 'sbds_op_escrow_transfers'
    __operation_type__ = 'escrow_transfer_operation'

    _from = Column('from',String(50), ForeignKey('sbds_meta_accounts.name')) # name:from
    to = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    agent = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    escrow_id = Column(Numeric) # steem_type:uint32_t
    sbd_amount = Column(Numeric(20,6), nullable=False) # steem_type:asset
    sbd_amount_symbol = Column(String(5)) # steem_type:asset
    steem_amount = Column(Numeric(20,6), nullable=False) # steem_type:asset
    steem_amount_symbol = Column(String(5)) # steem_type:asset
    fee = Column(Numeric(20,6), nullable=False) # steem_type:asset
    fee_symbol = Column(String(5)) # steem_type:asset
    ratification_deadline = Column(DateTime) # steem_type:time_point_sec
    escrow_expiration = Column(DateTime) # steem_type:time_point_sec
    json_meta = Column(JSONB) # name:json_meta
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='escrow_transfer')

    _fields = dict(
        sbd_amount=lambda x: amount_field(x.get('sbd_amount'), num_func=float), # steem_type:asset
        sbd_amount_symbol=lambda x: amount_symbol_field(x.get('sbd_amount')), # steem_type:asset
        steem_amount=lambda x: amount_field(x.get('steem_amount'), num_func=float), # steem_type:asset
        steem_amount_symbol=lambda x: amount_symbol_field(x.get('steem_amount')), # steem_type:asset
        fee=lambda x: amount_field(x.get('fee'), num_func=float), # steem_type:asset
        fee_symbol=lambda x: amount_symbol_field(x.get('fee')), # steem_type:asset
        ratification_deadline=lambda x: dateutil.parser.parse(x.get('ratification_deadline')), # steem_type:time_point_sec
        escrow_expiration=lambda x: dateutil.parser.parse(x.get('escrow_expiration')), # steem_type:time_point_sec
        json_meta=lambda x: json_string_field(x.get('json_meta')), # name:json_meta
    )


