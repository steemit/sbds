# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import accounts_field


class SetWithdrawVestingRouteOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "percent": 10000,
      "to_account": "newyo",
      "auto_vest": true,
      "from_account": "newyo6"
    }



    """

    __tablename__ = 'sbds_op_set_withdraw_vesting_routes'
    __table_args__ = (ForeignKeyConstraint(
        ['from_account'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        ForeignKeyConstraint(
        ['to_account'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        UniqueConstraint('block_num', 'transaction_num',
                         'operation_num', 'raw'),
        Index(
        'ix_sbds_op_set_withdraw_vesting_routes_accounts',
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

    from_account = Column(Text, nullable=True)  # steem_type:account_name_type
    to_account = Column(Text, nullable=True)  # steem_type:account_name_type
    percent = Column(Integer)  # steem_type:uint16_t
    auto_vest = Column(Boolean)  # steem_type:bool
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        accounts=lambda x: accounts_field(x, 'set_withdraw_vesting_route'), )

    _account_fields = frozenset([
        'from_account',
        'to_account',
    ])
