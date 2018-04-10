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

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field


class CustomBinaryOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_custom_binaries'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),





        Index('ix_sbds_op_custom_binaries_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    required_owner_auths = Column(JSONB)  # steem_type:flat_set< account_name_type>
    required_active_auths = Column(JSONB)  # steem_type:flat_set< account_name_type>
    required_posting_auths = Column(JSONB)  # steem_type:flat_set< account_name_type>
    required_auths = Column(JSONB)  # steem_type:vector< authority>
    id = Column(UnicodeText)  # steem_type:string -> default
    data = Column(String(100))  # steem_type:vector< char>
    operation_type = Column(operation_types_enum, nullable=False, default='custom_binary')

    _fields = dict(
        required_owner_auths=lambda x: json_string_field(
            x.get('required_owner_auths')),
        # steem_type:flat_set< account_name_type>
        required_active_auths=lambda x: json_string_field(
            x.get('required_active_auths')),
        # steem_type:flat_set< account_name_type>
        required_posting_auths=lambda x: json_string_field(
            x.get('required_posting_auths')),
        # steem_type:flat_set< account_name_type>
        required_auths=lambda x: json_string_field(
            x.get('required_auths')),  # steem_type:vector< authority>
        accounts=lambda x: sbds.sbds_json.dumps([acct for acct in set(flatten((x.get(
            'required_owner_auths'), x.get('required_active_auths'), x.get('required_posting_auths'),))) if acct])
    )

    _account_fields = frozenset(
        ['required_owner_auths', 'required_active_auths', 'required_posting_auths', ])
