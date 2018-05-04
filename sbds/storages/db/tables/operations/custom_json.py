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


class CustomJsonOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "required_auths": [],
      "id": "follow",
      "json": "{\"follower\":\"steemit\",\"following\":\"steem\",\"what\":[\"posts\"]}",
      "required_posting_auths": [
        "steemit"
      ]
    }



    """

    __tablename__ = 'sbds_op_custom_jsons'
    __table_args__ = (Index(
        'ix_sbds_sbds_op_custom_jsons_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True),
        Index(
        'ix_sbds_op_custom_jsons_accounts',
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
    required_posting_auths = Column(
        JSONB)  # steem_type:flat_set< account_name_type>
    id = Column(UnicodeText)  # steem_type:string -> default
    json = Column(JSONB)  # name:json
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        required_auths=lambda x: json_string_field(x.get('required_auths')),
        # steem_type:flat_set< account_name_type>
        required_posting_auths=lambda x: json_string_field(x.get('required_posting_auths')),
        # steem_type:flat_set< account_name_type>
        json=lambda x: json_string_field(x.get('json')),  # name:json
        accounts=lambda x: accounts_field(x, 'custom_json'),
    )

    _account_fields = frozenset([
        'required_auths',
        'required_posting_auths',
    ])
