# -*- coding: utf-8 -*-
from .views import view

'''
def should_create(ddl, target, connection, **kw):
    row = connection.execute(
        "select conname from pg_constraint where conname='%s'" %
        ddl.element.name).scalar()
    return not bool(row)

def should_drop(ddl, target, connection, **kw):
    return not should_create(ddl, target, connection, **kw)

event.listen(
    users,
    "after_create",
    DDL(
        "ALTER TABLE users ADD CONSTRAINT "
        "cst_user_name_length CHECK (length(user_name) >= 8)"
    ).execute_if(callable_=should_create)
)
event.listen(
    users,
    "before_drop",
    DDL(
        "ALTER TABLE users DROP CONSTRAINT cst_user_name_length"
    ).execute_if(callable_=should_drop)
)

SQLusers.create(engine)

SQLusers.drop(engine)
'''


ALL_OPERATIONS_SELECT_SQL = '''
    
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_creates
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_create_with_delegations
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_updates
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_comments
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_comment_option
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_challenge_authorities
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_prove_authorities
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_delete_comments
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_votes
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfers
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_transfers
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_approves
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_disputes
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_releases
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfer_to_vestings
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_withdraw_vestings
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_set_withdraw_vesting_routes
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_witness_updates
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_witness_votes
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_witness_proxies
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_customs
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_custom_jsons
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_custom_binaries
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_feed_publishes
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_converts
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_limit_order_creates
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_limit_order_create2s
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_limit_order_cancels
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_pows
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_pow2s
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_report_over_productions
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_request_account_recoveries
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_recover_accounts
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_reset_accounts
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_set_reset_accounts
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_change_recovery_accounts
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfer_to_saving
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfer_from_saving
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_cancel_transfer_from_saving
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_decline_voting_right
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_claim_reward_balances
        UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_delegate_vesting_share
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_author_rewards
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_curation_rewards
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_comment_rewards
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_liquidity_rewards
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_interests
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_convert_requests
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_vesting_withdraws
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_shutdown_witnesses
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_orders
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_transfer_from_saving
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_hardforks
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_comment_payout_updates
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_return_vesting_delegations
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_comment_benefactor_rewards
        UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_producer_rewards
        ;
'''

REAL_OPERATIONS_SELECT_SQL = '''
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_creates
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_create_with_delegations
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_updates
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_comments
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_comment_option
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_challenge_authorities
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_prove_authorities
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_delete_comments
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_votes
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfers
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_transfers
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_approves
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_disputes
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_escrow_releases
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfer_to_vestings
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_withdraw_vestings
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_set_withdraw_vesting_routes
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_witness_updates
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_witness_votes
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_account_witness_proxies
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_customs
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_custom_jsons
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_custom_binaries
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_feed_publishes
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_converts
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_limit_order_creates
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_limit_order_create2s
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_limit_order_cancels
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_pows
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_pow2s
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_report_over_productions
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_request_account_recoveries
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_recover_accounts
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_reset_accounts
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_set_reset_accounts
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_change_recovery_accounts
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfer_to_saving
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_transfer_from_saving
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_cancel_transfer_from_saving
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_decline_voting_right
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_claim_reward_balances
    UNION ALL
    SELECT block_num,transaction_num,operation_num,trx_id as id,operation_type FROM sbds_op_delegate_vesting_share
    
    ;
'''

VIRTUAL_OPERATIONS_SELECT_SQL = '''
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_author_rewards
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_curation_rewards
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_comment_rewards
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_liquidity_rewards
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_interests
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_convert_requests
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_vesting_withdraws
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_shutdown_witnesses
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_orders
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_fill_transfer_from_saving
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_hardforks
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_comment_payout_updates
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_return_vesting_delegations
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_comment_benefactor_rewards
    UNION ALL
    SELECT block_num,transaction_num,operation_num,id::text as id,operation_type FROM sbds_op_virtual_producer_rewards
    
    ;
'''


def create_operations_view():
    from sbds.storages.db.tables import metadata
    operations_view = view('sbds_views_operations',metadata, OPERATIONS_SELECT_SQL)

create_operations_view()

