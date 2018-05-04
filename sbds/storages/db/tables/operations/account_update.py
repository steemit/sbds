# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field
from ...field_handlers import json_string_field


class AccountUpdateOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "json_metadata": "",
      "account": "theoretical",
      "memo_key": "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
      "posting": {
        "key_auths": [
          [
            "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
            1
          ],
          [
            "STM76EQNV2RTA6yF9TnBvGSV71mW7eW36MM7XQp24JxdoArTfKA76",
            1
          ]
        ],
        "account_auths": [],
        "weight_threshold": 1
      }
    }



    """

    __tablename__ = 'sbds_op_account_updates'
    __table_args__ = (ForeignKeyConstraint(
        ['account'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        Index(
        'ix_sbds_sbds_op_account_updates_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True),
        Index(
        'ix_sbds_op_account_updates_accounts',
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

    account = Column(Text, nullable=True)  # steem_type:account_name_type
    owner = Column(JSONB)  # steem_type:optional< authority>
    active = Column(JSONB)  # steem_type:optional< authority>
    posting = Column(JSONB)  # steem_type:optional< authority>
    memo_key = Column(Text, nullable=False)  # steem_type:public_key_type
    json_metadata = Column(JSONB)  # name:json_metadata
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        owner=lambda x: json_string_field(x.get('owner')),  # steem_type:optional< authority>
        active=lambda x: json_string_field(x.get('active')),  # name:active
        posting=lambda x: json_string_field(x.get('posting')),  # name:posting
        json_metadata=lambda x: json_string_field(x.get('json_metadata')),  # name:json_metadata
        accounts=lambda x: accounts_field(x, 'account_update'),
    )

    _account_fields = frozenset([
        'account',
    ])
