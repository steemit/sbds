# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.schema import Index
from sqlalchemy.schema import Table
from sqlalchemy.types import BIGINT
from sqlalchemy.types import DATETIME
from sqlalchemy.types import Enum
from sqlalchemy.types import INTEGER
from sqlalchemy.types import SMALLINT
from sqlalchemy.types import TEXT
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import JSON
meta = MetaData()

blocks_table = Table('sbds_blocks', meta,
                     Column('raw', JSON, nullable=False),
                     Column('block_num',
                            INTEGER(),
                            primary_key=True,
                            nullable=False,
                            autoincrement=False),
                     Column('previous', VARCHAR(length=50)),
                     Column('timestamp', DATETIME()),
                     Column('witness', VARCHAR(length=50)),
                     Column('witness_signature', VARCHAR(length=150)),
                     Column('transaction_merkle_root', VARCHAR(length=50)),
                     Column('extensions', JSON),
                     Column('transactions', JSON),
                     mysql_engine='InnoDB',
                     mysql_charset='utf8',
                     mysql_collate='utf8_general_ci'
                     )

transaction_types_enum = Enum(
        'vote',
        'comment',
        'transfer',
        'transfer_to_vesting',
        'withdraw_vesting',
        'limit_order_create',
        'limit_order_cancel',
        'feed_publish',
        'convert',
        'account_create',
        'account_update',
        'witness_update',
        'account_witness_vote',
        'account_witness_proxy',
        'pow',
        'custom',
        'report_over_production',
        'delete_comment',
        'custom_json',
        'comment_options',
        'set_withdraw_vesting_route',
        'limit_order_create2',
        'challenge_authority',
        'prove_authority',
        'request_account_recovery',
        'recover_account',
        'change_recovery_account',
        'escrow_transfer',
        'escrow_dispute',
        'escrow_release',
        'pow2',
        'escrow_approve',
        'transfer_to_savings',
        'transfer_from_savings',
        'cancel_transfer_from_savings',
        'custom_binary_operation',
        'decline_voting_rights_operation',
        'reset_account_operation',
        'set_reset_account_operation')

transactions_table = Table('sbds_transactions', meta,
                           Column('txid',
                                  INTEGER(),
                                  primary_key=True,
                                  autoincrement=True
                                  ),
                           Column('block_num',
                                  INTEGER(),
                                  nullable=False),
                           Column('transaction_num',
                                  SMALLINT(),
                                  nullable=False),

                           Column('ref_block_num',
                                  INTEGER(),
                                  nullable=False),
                           Column('ref_block_prefix',
                                  BIGINT(),
                                  nullable=False),
                           Column('expiration',
                                  DATETIME(),
                                  nullable=False),
                           Column('type',
                                  transaction_types_enum,
                                  nullable=False,
                                  index=True),
                           Column('operations',
                                  JSON),
                           Column('extensions',
                                  JSON),
                           Column('signatures',
                                  JSON),
                           ForeignKeyConstraint(columns=['block_num'],
                                                refcolumns=[blocks_table.c.block_num],
                                                use_alter=True,
                                                ondelete="CASCADE",
                                                onupdate="CASCADE"),
                           Index('tx_index', 'block_num', 'transaction_num', unique=True),
                           mysql_engine='InnoDB',
                           mysql_charset='utf8',
                           mysql_collate='utf8_general_ci'
                           )
