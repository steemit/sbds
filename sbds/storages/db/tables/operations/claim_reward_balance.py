# -*- coding: utf-8 -*-

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from .. import Base
from ...enums import asset_types_enum
from ...enums import operation_types_enum
from ...field_handlers import accounts_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field


class ClaimRewardBalanceOperation(Base):
    """

    Steem Blockchain Example
    ======================
    {
      "reward_steem": "0.017 STEEM",
      "reward_vests": "185.025103 VESTS",
      "account": "ocrdu",
      "reward_sbd": "0.011 SBD"
    }



    """

    __tablename__ = 'sbds_op_claim_reward_balances'
    __table_args__ = (ForeignKeyConstraint(
        ['account'], ['sbds_meta_accounts.name'],
        deferrable=True,
        initially='DEFERRED',
        use_alter=True),
        UniqueConstraint('block_num', 'transaction_num',
                         'operation_num', 'raw'),
        Index(
        'ix_sbds_op_claim_reward_balances_accounts',
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
    reward_steem = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    reward_steem_symbol = Column(
        asset_types_enum, nullable=False)  # steem_type:asset
    reward_sbd = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    reward_sbd_symbol = Column(
        asset_types_enum, nullable=False)  # steem_type:asset
    reward_vests = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    reward_vests_symbol = Column(
        asset_types_enum, nullable=False)  # steem_type:asset
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        reward_steem=lambda x: amount_field(
            x.get('reward_steem'), num_func=float),  # steem_type:asset
        reward_steem_symbol=lambda x: amount_symbol_field(
            x.get('reward_steem')),  # steem_type:asset
        reward_sbd=lambda x: amount_field(x.get('reward_sbd'), num_func=float),  # steem_type:asset
        reward_sbd_symbol=lambda x: amount_symbol_field(x.get('reward_sbd')),  # steem_type:asset
        reward_vests=lambda x: amount_field(
            x.get('reward_vests'), num_func=float),  # steem_type:asset
        reward_vests_symbol=lambda x: amount_symbol_field(
            x.get('reward_vests')),  # steem_type:asset
        accounts=lambda x: accounts_field(x, 'claim_reward_balance'),
    )

    _account_fields = frozenset([
        'account',
    ])
