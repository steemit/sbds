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


class EscrowReleaseOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "who": "xtar",
      "sbd_amount": "5.000 SBD",
      "steem_amount": "0.000 STEEM",
      "from": "anonymtest",
      "agent": "xtar",
      "to": "someguy123",
      "escrow_id": 72526562,
      "receiver": "someguy123"
    }



    """

    __tablename__ = 'sbds_op_escrow_releases'
    __operation_type__ = 'escrow_release_operation'

    _from = Column('from', String(50), ForeignKey('sbds_meta_accounts.name'))  # name:from
    to = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    agent = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    who = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    receiver = Column(String(50), ForeignKey("sbds_meta_accounts.name"))  # steem_type:account_name_type
    escrow_id = Column(Integer)  # steem_type:uint32_t
    sbd_amount = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    sbd_amount_symbol = Column(String(5))  # steem_type:asset
    steem_amount = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    steem_amount_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='escrow_release_operation')

    _fields = dict(
        sbd_amount=lambda x: amount_field(x.get('sbd_amount'), num_func=float),
        sbd_amount_symbol=lambda x: amount_symbol_field(x.get('sbd_amount')),
        steem_amount=lambda x: amount_field(x.get('steem_amount'), num_func=float),
        steem_amount_symbol=lambda x: amount_symbol_field(x.get('steem_amount')),
    )
