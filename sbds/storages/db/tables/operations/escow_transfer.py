# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from .base import BaseOperation


class EscrowTransferOperation(Base, BaseOperation):
    """
    Raw Format
    ==========
    {
     "from": "siol",
     "agent": "fabien",
     "escrow_expiration": "2017-02-28T11:22:39",
     "to": "james",
     "ratification_deadline": "2017-02-26T11:22:39",
     "escrow_id": 23456789,
     "steem_amount": "0.000 STEEM",
     "json_meta": "{}",
     "sbd_amount": "1.000 SBD",
     "fee": "0.100 SBD"
    }
    """

    __tablename__ = 'sbds_op_escrow_transfers'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    _from = Column('from', Unicode(50), index=True)
    agent = Column(Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    escrow_id = Column(Integer)
    steem_amount = Column(Numeric(15, 6))
    sbd_amount = Column(Numeric(15, 6))

    json_metadata = Column(UnicodeText)
    fee_amount = Column(Numeric(15, 6))
    fee_amount_symbol = Column(Unicode(5))
    escrow_expiration = Column(DateTime(timezone=False), index=True)
    ratification_deadline = Column(DateTime(timezone=False), index=True)

    _fields = dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        escrow_id=lambda x: x.get('request_id'),
        sbd_amount=lambda x: amount_field(x.get('sbd_amount'), num_func=float),
        steem_amount=lambda x: amount_field(x.get('steem_amount'), num_func=float),
        fee_amount=lambda x: amount_field(x.get('fee'), num_func=float),
        fee_amount_symbol=lambda x: amount_symbol_field(x.get('fee')),
        json_metadata=lambda x: x.get('json_meta'),
        escrow_expiration=lambda x: x.get('escrow_expiration'),
        ratification_deadline=lambda x: x.get('ratification_deadline'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='escrow_transfer')
