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

from ...import Base
from ....enums import operation_types_enum
from ....field_handlers import json_string_field
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field


class FillConvertRequestVirtualOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_fill_convert_requests'
    __table_args__ = (


        ForeignKeyConstraint(['owner'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_virtual_fill_convert_requests_accounts', 'accounts', postgresql_using='gin')

    )

    id = Column(Integer, primary_key=True)

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(ARRAY(String(16)))
    owner = Column(String(16), nullable=True)  # steem_type:account_name_type
    requestid = Column(Numeric)  # steem_type:uint32_t
    amount_in = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    amount_in_symbol = Column(String(5))  # steem_type:asset
    amount_out = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    amount_out_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(operation_types_enum, nullable=False, default='fill_convert_request')

    _fields = dict(
        amount_in=lambda x: amount_field(x.get('amount_in'), num_func=float),  # steem_type:asset
        amount_in_symbol=lambda x: amount_symbol_field(x.get('amount_in')),  # steem_type:asset
        amount_out=lambda x: amount_field(x.get('amount_out'), num_func=float),  # steem_type:asset
        amount_out_symbol=lambda x: amount_symbol_field(x.get('amount_out')),  # steem_type:asset
        accounts=lambda x: tuple(flatten((x.get('owner'),)))
    )

    _account_fields = frozenset(['owner', ])
