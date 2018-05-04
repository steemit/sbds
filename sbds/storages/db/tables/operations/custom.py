# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UnicodeText
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field
from ...field_handlers import json_string_field


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
    __table_args__ = (Index(
        'ix_sbds_sbds_op_customs_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True),
        Index(
        'ix_sbds_op_customs_accounts',
        'accounts',
        postgresql_using='gin',
        postgresql_ops={'accounts': 'jsonb_path_ops'}))

    _id = Column(BigInteger, autoincrement=True, primary_key=True)
    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False))
    trx_id = Column(Text, nullable=False)
    accounts = Column(JSONB)
    raw = Column(JSONB)

    required_auths = Column(JSONB)  # steem_type:flat_set< account_name_type>
    id = Column(Integer)  # steem_type:uint16_t
    data = Column(UnicodeText)  # steem_type:vector< char>
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        required_auths=lambda x: json_string_field(x.get('required_auths')),
        # steem_type:flat_set< account_name_type>
        accounts=lambda x: accounts_field(x, 'custom'),
    )

    _account_fields = frozenset([
        'required_auths',
    ])
