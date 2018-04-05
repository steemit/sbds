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

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field


class ResetAccountOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_reset_accounts'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['reset_account'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),



        ForeignKeyConstraint(['account_to_reset'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_reset_accounts_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(ARRAY(String(16)))
    reset_account = Column(String(16), nullable=True)  # steem_type:account_name_type
    account_to_reset = Column(String(16), nullable=True)  # steem_type:account_name_type
    new_owner_authority = Column(JSONB)  # steem_type:authority
    operation_type = Column(operation_types_enum, nullable=False, default='reset_account')

    _fields = dict(
        new_owner_authority=lambda x: json_string_field(
            x.get('new_owner_authority')),  # steem_type:authority
        accounts=lambda x: tuple(flatten((x.get('reset_account'), x.get('account_to_reset'),)))
    )

    _account_fields = frozenset(['reset_account', 'account_to_reset', ])
