# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Integer, Boolean, Enum

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class EscrowDisputeOperation(Base, BaseOperation):
    """
    Raw Format
    ==========
    {
        "escrow_id": 72526562,
        "from": "anonymtest",
        "agent": "xtar",
        "who": "anonymtest",
        "to": "someguy123"
    }
    """

    __tablename__ = 'sbds_op_escrow_disputes'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    _from = Column('from', Unicode(50), index=True)
    agent = Column(Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    who = Column(Unicode(50), index=True)
    escrow_id = Column(Integer)
    approve = Column(Boolean)

    _fields = dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        escrow_id=lambda x: x.get('request_id'),
        who=lambda x: x.get('who')
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

