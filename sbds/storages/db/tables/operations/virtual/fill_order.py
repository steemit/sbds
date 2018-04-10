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

from ...import Base
from ....enums import operation_types_enum
from ....field_handlers import json_string_field
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field


class FillOrderVirtualOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_fill_orders'
    __table_args__ = (


        ForeignKeyConstraint(['current_owner'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),



        ForeignKeyConstraint(['open_owner'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_virtual_fill_orders_accounts', 'accounts', postgresql_using='gin')

    )

    id = Column(Integer, primary_key=True)

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    current_owner = Column(String(16), nullable=True)  # steem_type:account_name_type
    current_orderid = Column(Numeric)  # steem_type:uint32_t
    current_pays = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    current_pays_symbol = Column(String(5))  # steem_type:asset
    open_owner = Column(String(16), nullable=True)  # steem_type:account_name_type
    open_orderid = Column(Numeric)  # steem_type:uint32_t
    open_pays = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    open_pays_symbol = Column(String(5))  # steem_type:asset
    operation_type = Column(operation_types_enum, nullable=False, default='fill_order')

    _fields = dict(
        current_pays=lambda x: amount_field(
            x.get('current_pays'), num_func=float),  # steem_type:asset
        current_pays_symbol=lambda x: amount_symbol_field(
            x.get('current_pays')),  # steem_type:asset
        open_pays=lambda x: amount_field(x.get('open_pays'), num_func=float),  # steem_type:asset
        open_pays_symbol=lambda x: amount_symbol_field(x.get('open_pays')),  # steem_type:asset
        accounts=lambda x: sbds.sbds_json.dumps([acct for acct in set(
            flatten((x.get('current_owner'), x.get('open_owner'),))) if acct])
    )

    _account_fields = frozenset(['current_owner', 'open_owner', ])
