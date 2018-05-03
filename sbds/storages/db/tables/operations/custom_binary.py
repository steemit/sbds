# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field
from ...field_handlers import binary_field
from ...field_handlers import json_string_field


class CustomBinaryOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_custom_binaries'
    __table_args__ = (UniqueConstraint('block_num', 'transaction_num',
                                       'operation_num', 'raw'),
                      Index(
                          'ix_sbds_op_custom_binaries_accounts',
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

    required_owner_auths = Column(
        JSONB)  # steem_type:flat_set< account_name_type>
    required_active_auths = Column(
        JSONB)  # steem_type:flat_set< account_name_type>
    required_posting_auths = Column(
        JSONB)  # steem_type:flat_set< account_name_type>
    required_auths = Column(JSONB)  # steem_type:vector< authority>
    id = Column(UnicodeText)  # steem_type:string -> default
    data = Column(BYTEA())  # name: data,custom_binary_operation vector< char>
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        required_owner_auths=lambda x: json_string_field(x.get('required_owner_auths')),
        # steem_type:flat_set< account_name_type>
        required_active_auths=lambda x: json_string_field(x.get('required_active_auths')),
        # steem_type:flat_set< account_name_type>
        required_posting_auths=lambda x: json_string_field(x.get('required_posting_auths')),
        # steem_type:flat_set< account_name_type>
        required_auths=lambda x: json_string_field(
            x.get('required_auths')),  # steem_type:vector< authority>
        data=lambda x: binary_field(x.get('data')),
        # name: data,custom_binary_operation vector< char>
        accounts=lambda x: accounts_field(x, 'custom_binary'),
    )

    _account_fields = frozenset([
        'required_owner_auths',
        'required_active_auths',
        'required_posting_auths',
    ])
