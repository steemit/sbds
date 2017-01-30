# -*- coding: utf-8 -*-
from sqlalchemy.types import Enum

transaction_types_enum = Enum(
        'account_create',
        'account_update',
        'account_witness_proxy',
        'account_witness_vote',
        'cancel_transfer_from_savings',
        'challenge_authority',
        'change_recovery_account',
        'comment',
        'comment_options',
        'convert',
        'custom',
        'custom_binary_operation',
        'custom_json',
        'decline_voting_rights_operation',
        'delete_comment',
        'escrow_approve',
        'escrow_dispute',
        'escrow_release',
        'escrow_transfer',
        'feed_publish',
        'limit_order_cancel',
        'limit_order_create',
        'limit_order_create2',
        'pow',
        'pow2',
        'prove_authority',
        'recover_account',
        'report_over_production',
        'request_account_recovery',
        'reset_account_operation',
        'set_reset_account_operation',
        'set_withdraw_vesting_route',
        'transfer',
        'transfer_from_savings',
        'transfer_to_savings',
        'transfer_to_vesting',
        'vote',
        'withdraw_vesting',
        'witness_update',
        name='sbds_transaction_types')

comment_types_enum = Enum(
        'post',
        'comment',
        name='sbds_comment_types'
)

extraction_source_enum = Enum(
        'body',
        'meta',
        name='sbds_extraction_sources'
)
