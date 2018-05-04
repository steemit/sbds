# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text

from ... import Base
from ....enums import operation_types_enum


class HardforkVirtualOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_hardforks'
    __table_args__ = (
        # not yet supported Index('block_num', 'transaction_num',
        # 'operation_num','op_virtual', unique=True),
        Index(
            'ix_sbds_sbds_op_virtual_hardforks_unique',
            'block_num',
            'transaction_num',
            'operation_num',
            text("MD5('raw')"),
            unique=True), )

    _id = Column(BigInteger, autoincrement=True, primary_key=True)
    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(Text, nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    hardfork_id = Column(Numeric)  # steem_type:uint32_t
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict()

    _account_fields = frozenset([])
