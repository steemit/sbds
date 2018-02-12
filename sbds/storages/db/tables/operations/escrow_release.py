# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from .base import BaseOperation


class EscrowReleaseOperation(Base, BaseOperation):
    """
    Raw Format
    ==========
    {
        "from": "anonymtest",
        "agent": "xtar",
        "to": "someguy123",
        "escrow_id": 72526562,
        "steem_amount": "0.000 STEEM",
        "sbd_amount": "5.000 SBD",
        "who": "xtar",
        "receiver": "someguy123"
    }
    """

    __tablename__ = 'sbds_op_escrow_releases'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    _from = Column('from', Unicode(50), index=True)
    agent = Column(Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    escrow_id = Column(Integer)
    steem_amount = Column(Numeric(15, 6))
    sbd_amount = Column(Numeric(15, 6))
    who = Column(Unicode(50), index=True)
    receiver = Column(Unicode(50), index=True)

    _fields = dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        who=lambda x: x.get('who'),
        receiver=lambda x: x.get('receiver'),
        escrow_id=lambda x: x.get('request_id'),
        sbd_amount=lambda x: amount_field(x.get('sbd_amount'), num_func=float),
        steem_amount=lambda x: amount_field(x.get('steem_amount'), num_func=float))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
