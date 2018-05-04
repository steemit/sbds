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


class ReportOverProductionOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_report_over_productions'
    __table_args__ = (ForeignKeyConstraint(
        ['reporter'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        Index(
        'ix_sbds_sbds_op_report_over_productions_unique',
        'block_num',
        'transaction_num',
        'operation_num',
        unique=True),
        Index(
        'ix_sbds_op_report_over_productions_accounts',
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

    reporter = Column(Text, nullable=True)  # steem_type:account_name_type
    first_block = Column(JSONB)  # steem_type:signed_block_header
    second_block = Column(JSONB)  # steem_type:signed_block_header
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        first_block=lambda x: json_string_field(
            x.get('first_block')),  # steem_type:signed_block_header
        second_block=lambda x: json_string_field(
            x.get('second_block')),  # steem_type:signed_block_header
        accounts=lambda x: accounts_field(x, 'report_over_production'),
    )

    _account_fields = frozenset([
        'reporter',
    ])
