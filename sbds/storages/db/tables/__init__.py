# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.schema import Index
from sqlalchemy.schema import Table
from sqlalchemy.types import BIGINT
from sqlalchemy.types import TIMESTAMP

from sqlalchemy.types import Enum
from sqlalchemy.types import INTEGER
from sqlalchemy.types import SMALLINT
from sqlalchemy.types import TEXT
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import JSON
meta = MetaData()
from sqlalchemy.orm import mapper
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB


blocks_table = Table('sbds_blocks', meta,
                     Column('raw', JSONB, nullable=False),
                     Column('block_num',
                            INTEGER(),
                            primary_key=True,
                            nullable=False,
                            autoincrement=False),
                     Column('previous', VARCHAR(length=50)),
                     Column('timestamp', TIMESTAMP(timezone=False), index=True),
                     Column('witness', VARCHAR(length=50)),
                     Column('witness_signature', VARCHAR(length=150)),
                     Column('transaction_merkle_root', VARCHAR(length=50)),
                     Column('extensions', JSONB),
                     mysql_engine='InnoDB',
                     mysql_charset='utf8',
                     mysql_collate='utf8_general_ci'
                     )

class Block(object):

    def __repr__(self):
        return "<Block(block_num='%s', timestamp='%s')>" % (
        self.block_num, self.timestamp)

mapper(Block, blocks_table)

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
        'set_reset_account_operation',
        name='sbds_transaction_types',
        metadata=meta)


transactions_table = Table('sbds_transactions', meta,
                           Column('tx_id',
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
                                  TIMESTAMP(timezone=False),
                                  nullable=False),
                           Column('type',
                                  transaction_types_enum,
                                  nullable=False,
                                  index=True),
                           Column('op_count',
                                  SMALLINT(),
                                  default=0),
                           Column('operations',
                                  JSONB),
                           Column('extensions',
                                  JSONB),
                           Column('signatures',
                                  JSONB),
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


class Transaction(object):

    def __repr__(self):
        return "<Transaction(block_num='%s', transaction_num='%s' op_type='%s')>" % (
            self.block_num, self.transaction_num, self.type)

mapper(Transaction, transactions_table, properties={
    'block' : relationship(Block, backref='transactions')})


operations_table = Table('sbds_operations', meta,
                        Column('op_id',INTEGER(),
                               primary_key=True,
                                nullable=False,
                                autoincrement=True),
                        Column('block_num',INTEGER(),nullable=False),
                        Column('transaction_num', SMALLINT(), nullable=False),
                        Column('operation_num', SMALLINT(), nullable=False),
                        Column('timestamp', TIMESTAMP(timezone=False), index=True),
                        Column('op_type', transaction_types_enum, nullable=False, index=True),
                        Column('op_meta', JSONB()),
)

class Operation(object):

    def __repr__(self):
        return "<Operation(op_type='%s' block_num='%s', transaction_num='%s' op_id='%s')>" % (
            self.type, self.block_num, self.transaction_num, self.op_id)