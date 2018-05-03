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
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from ... import Base
from ....enums import asset_types_enum
from ....enums import operation_types_enum
from ....field_handlers import accounts_field
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field


class CommentBenefactorRewardVirtualOperation(Base):
    """

    Steem Blockchain Example
    ======================




    """

    __tablename__ = 'sbds_op_virtual_comment_benefactor_rewards'
    __table_args__ = (
        ForeignKeyConstraint(
            ['benefactor'], ['sbds_meta_accounts.name'],
            deferrable=True,
            initially='DEFERRED',
            use_alter=True),
        ForeignKeyConstraint(
            ['author'], ['sbds_meta_accounts.name'],
            deferrable=True,
            initially='DEFERRED',
            use_alter=True),
        UniqueConstraint('block_num', 'transaction_num', 'operation_num',
                         'raw'),
        Index(
            'ix_sbds_op_virtual_comment_benefactor_rewards_accounts',
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

    benefactor = Column(Text, nullable=True)  # steem_type:account_name_type
    author = Column(Text, nullable=True)  # steem_type:account_name_type
    permlink = Column(UnicodeText, index=True)  # name:permlink
    reward = Column(Numeric(20, 6), nullable=False)  # steem_type:asset
    reward_symbol = Column(
        asset_types_enum, nullable=False)  # steem_type:asset
    operation_type = Column(operation_types_enum, nullable=False, default='')

    _fields = dict(
        reward=lambda x: amount_field(x.get('reward'), num_func=float),  # steem_type:asset
        reward_symbol=lambda x: amount_symbol_field(x.get('reward')),  # steem_type:asset
        accounts=lambda x: accounts_field(x, 'comment_benefactor_reward'),
    )

    _account_fields = frozenset([
        'benefactor',
        'author',
    ])
