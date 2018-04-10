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


class AccountWitnessVoteOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "account": "donalddrumpf",
      "approve": true,
      "witness": "berniesanders"
    }



    """

    __tablename__ = 'sbds_op_account_witness_votes'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        ForeignKeyConstraint(['account'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),



        ForeignKeyConstraint(['witness'], ['sbds_meta_accounts.name'],
                             deferrable=True, initially='DEFERRED', use_alter=True),

        Index('ix_sbds_op_account_witness_votes_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    account = Column(String(16), nullable=True)  # steem_type:account_name_type
    witness = Column(String(16), nullable=True)  # steem_type:account_name_type
    approve = Column(Boolean)  # steem_type:bool
    operation_type = Column(operation_types_enum, nullable=False, default='account_witness_vote')

    _fields = dict(
        accounts=lambda x: sbds.sbds_json.dumps([acct for acct in set(
            flatten((x.get('account'), x.get('witness'),))) if acct])
    )

    _account_fields = frozenset(['account', 'witness', ])
