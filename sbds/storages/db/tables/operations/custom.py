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


class CustomOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "id": 0,
      "data": "276e1c988628df33",
      "required_auths": [
        "blocktrades"
      ]
    }



    """

    __tablename__ = 'sbds_op_customs'
    __table_args__ = (
        PrimaryKeyConstraint('block_num', 'transaction_num', 'operation_num'),

        Index('ix_sbds_op_customs_accounts', 'accounts', postgresql_using='gin')

    )

    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(String(40), nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    required_auths = Column(JSONB)  # steem_type:flat_set< account_name_type>
    id = Column(Integer)  # steem_type:uint16_t
    data = Column(String(100))  # steem_type:vector< char>
    operation_type = Column(operation_types_enum, nullable=False, default='custom')

    _fields = dict(
        required_auths=lambda x: json_string_field(
            x.get('required_auths')),
        # steem_type:flat_set< account_name_type>
        accounts=lambda x: sbds.sbds_json.dumps(
            [acct for acct in set(flatten((x.get('required_auths'),))) if acct])
    )

    _account_fields = frozenset(['required_auths', ])
