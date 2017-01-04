# -*- coding: utf-8 -*-

import json

from sqlalchemy import MetaData
from sqlalchemy.schema import Table
from sqlalchemy.schema import Column
from sqlalchemy.types import JSON
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import DATETIME
from sqlalchemy.schema import ForeignKey
from sqlalchemy.dialects import mysql

from sbds.utils import block_num_from_previous

meta = MetaData()

blocks_table = Table('Blocks2', meta,
                    Column('raw', JSON(), nullable=False),
                    Column('block_num',
                           mysql.INTEGER(display_width=10, unsigned=True),
                           primary_key=True,
                           nullable=False,
                           autoincrement=False),
                    Column('previous', VARCHAR(length=50)),
                    Column('timestamp', DATETIME()),
                    Column('witness', VARCHAR(length=50)),
                    Column('witness_signature', VARCHAR(length=150)),
                    Column('transaction_merkle_root', VARCHAR(length=50)),
                    Column('extensions', JSON()),
                    Column('transactions', JSON()),
                    mysql_engine='InnoDB',
                    mysql_charset='utf8',
                    mysql_collate='utf8_general_ci'
                    )


transaction_types_enum = mysql.ENUM(
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

transactions_table = Table('Transactions4', meta,
                   Column('block_num',
                          mysql.INTEGER(display_width=10, unsigned=True),
                            ForeignKey('Blocks2.block_num',
                                       use_alter=True,
                                       onupdate="CASCADE",
                                       ondelete="CASCADE"),
                          primary_key=True,
                          autoincrement=False,
                          nullable=False),
                   Column('transaction_num',
                          mysql.TINYINT(display_width=3, unsigned=True),
                          primary_key=True,
                          nullable=False),
                   Column('ref_block_num',
                          mysql.INTEGER(display_width=10, unsigned=True),
                          nullable=False),
                   Column('ref_block_prefix',
                          mysql.BIGINT(display_width=20, unsigned=True),
                          nullable=False),
                   Column('expiration',
                          DATETIME(),
                          nullable=False),
                   Column('type',
                          transaction_types_enum,
                          nullable=False),
                    mysql_engine='InnoDB',
                    mysql_charset='utf8',
                    mysql_collate='utf8_general_ci'
                   )