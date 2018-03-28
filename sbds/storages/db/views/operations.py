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

BLOCKS_VIEW_SQL = '''
    SELECT sbds_core_blocks.block_num as block_num,
           sbds_core_blocks.timestamp as timestamp,

            sbds_op_account_creates.transaction_num as sbds_op_account_creates_tx_num,
            sbds_op_account_creates.operation_num as sbds_op_account_creates_op_num,
            sbds_op_account_creates.trx_id as sbds_op_account_creates_trx_id,
            0 as sbds_op_account_creates_virtual,
            sbds_op_account_creates.operation_type as sbds_op_account_creates_type,
            sbds_op_account_create_with_delegations.transaction_num as sbds_op_account_create_with_delegations_tx_num,
            sbds_op_account_create_with_delegations.operation_num as sbds_op_account_create_with_delegations_op_num,
            sbds_op_account_create_with_delegations.trx_id as sbds_op_account_create_with_delegations_trx_id,
            0 as sbds_op_account_create_with_delegations_virtual,
            sbds_op_account_create_with_delegations.operation_type as sbds_op_account_create_with_delegations_type,
            sbds_op_account_updates.transaction_num as sbds_op_account_updates_tx_num,
            sbds_op_account_updates.operation_num as sbds_op_account_updates_op_num,
            sbds_op_account_updates.trx_id as sbds_op_account_updates_trx_id,
            0 as sbds_op_account_updates_virtual,
            sbds_op_account_updates.operation_type as sbds_op_account_updates_type,
            sbds_op_comments.transaction_num as sbds_op_comments_tx_num,
            sbds_op_comments.operation_num as sbds_op_comments_op_num,
            sbds_op_comments.trx_id as sbds_op_comments_trx_id,
            0 as sbds_op_comments_virtual,
            sbds_op_comments.operation_type as sbds_op_comments_type,
            sbds_op_comment_option.transaction_num as sbds_op_comment_option_tx_num,
            sbds_op_comment_option.operation_num as sbds_op_comment_option_op_num,
            sbds_op_comment_option.trx_id as sbds_op_comment_option_trx_id,
            0 as sbds_op_comment_option_virtual,
            sbds_op_comment_option.operation_type as sbds_op_comment_option_type,
            sbds_op_challenge_authorities.transaction_num as sbds_op_challenge_authorities_tx_num,
            sbds_op_challenge_authorities.operation_num as sbds_op_challenge_authorities_op_num,
            sbds_op_challenge_authorities.trx_id as sbds_op_challenge_authorities_trx_id,
            0 as sbds_op_challenge_authorities_virtual,
            sbds_op_challenge_authorities.operation_type as sbds_op_challenge_authorities_type,
            sbds_op_prove_authorities.transaction_num as sbds_op_prove_authorities_tx_num,
            sbds_op_prove_authorities.operation_num as sbds_op_prove_authorities_op_num,
            sbds_op_prove_authorities.trx_id as sbds_op_prove_authorities_trx_id,
            0 as sbds_op_prove_authorities_virtual,
            sbds_op_prove_authorities.operation_type as sbds_op_prove_authorities_type,
            sbds_op_delete_comments.transaction_num as sbds_op_delete_comments_tx_num,
            sbds_op_delete_comments.operation_num as sbds_op_delete_comments_op_num,
            sbds_op_delete_comments.trx_id as sbds_op_delete_comments_trx_id,
            0 as sbds_op_delete_comments_virtual,
            sbds_op_delete_comments.operation_type as sbds_op_delete_comments_type,
            sbds_op_votes.transaction_num as sbds_op_votes_tx_num,
            sbds_op_votes.operation_num as sbds_op_votes_op_num,
            sbds_op_votes.trx_id as sbds_op_votes_trx_id,
            0 as sbds_op_votes_virtual,
            sbds_op_votes.operation_type as sbds_op_votes_type,
            sbds_op_transfers.transaction_num as sbds_op_transfers_tx_num,
            sbds_op_transfers.operation_num as sbds_op_transfers_op_num,
            sbds_op_transfers.trx_id as sbds_op_transfers_trx_id,
            0 as sbds_op_transfers_virtual,
            sbds_op_transfers.operation_type as sbds_op_transfers_type,
            sbds_op_escrow_transfers.transaction_num as sbds_op_escrow_transfers_tx_num,
            sbds_op_escrow_transfers.operation_num as sbds_op_escrow_transfers_op_num,
            sbds_op_escrow_transfers.trx_id as sbds_op_escrow_transfers_trx_id,
            0 as sbds_op_escrow_transfers_virtual,
            sbds_op_escrow_transfers.operation_type as sbds_op_escrow_transfers_type,
            sbds_op_escrow_approves.transaction_num as sbds_op_escrow_approves_tx_num,
            sbds_op_escrow_approves.operation_num as sbds_op_escrow_approves_op_num,
            sbds_op_escrow_approves.trx_id as sbds_op_escrow_approves_trx_id,
            0 as sbds_op_escrow_approves_virtual,
            sbds_op_escrow_approves.operation_type as sbds_op_escrow_approves_type,
            sbds_op_escrow_disputes.transaction_num as sbds_op_escrow_disputes_tx_num,
            sbds_op_escrow_disputes.operation_num as sbds_op_escrow_disputes_op_num,
            sbds_op_escrow_disputes.trx_id as sbds_op_escrow_disputes_trx_id,
            0 as sbds_op_escrow_disputes_virtual,
            sbds_op_escrow_disputes.operation_type as sbds_op_escrow_disputes_type,
            sbds_op_escrow_releases.transaction_num as sbds_op_escrow_releases_tx_num,
            sbds_op_escrow_releases.operation_num as sbds_op_escrow_releases_op_num,
            sbds_op_escrow_releases.trx_id as sbds_op_escrow_releases_trx_id,
            0 as sbds_op_escrow_releases_virtual,
            sbds_op_escrow_releases.operation_type as sbds_op_escrow_releases_type,
            sbds_op_transfer_to_vestings.transaction_num as sbds_op_transfer_to_vestings_tx_num,
            sbds_op_transfer_to_vestings.operation_num as sbds_op_transfer_to_vestings_op_num,
            sbds_op_transfer_to_vestings.trx_id as sbds_op_transfer_to_vestings_trx_id,
            0 as sbds_op_transfer_to_vestings_virtual,
            sbds_op_transfer_to_vestings.operation_type as sbds_op_transfer_to_vestings_type,
            sbds_op_withdraw_vestings.transaction_num as sbds_op_withdraw_vestings_tx_num,
            sbds_op_withdraw_vestings.operation_num as sbds_op_withdraw_vestings_op_num,
            sbds_op_withdraw_vestings.trx_id as sbds_op_withdraw_vestings_trx_id,
            0 as sbds_op_withdraw_vestings_virtual,
            sbds_op_withdraw_vestings.operation_type as sbds_op_withdraw_vestings_type,
            sbds_op_set_withdraw_vesting_routes.transaction_num as sbds_op_set_withdraw_vesting_routes_tx_num,
            sbds_op_set_withdraw_vesting_routes.operation_num as sbds_op_set_withdraw_vesting_routes_op_num,
            sbds_op_set_withdraw_vesting_routes.trx_id as sbds_op_set_withdraw_vesting_routes_trx_id,
            0 as sbds_op_set_withdraw_vesting_routes_virtual,
            sbds_op_set_withdraw_vesting_routes.operation_type as sbds_op_set_withdraw_vesting_routes_type,
            sbds_op_witness_updates.transaction_num as sbds_op_witness_updates_tx_num,
            sbds_op_witness_updates.operation_num as sbds_op_witness_updates_op_num,
            sbds_op_witness_updates.trx_id as sbds_op_witness_updates_trx_id,
            0 as sbds_op_witness_updates_virtual,
            sbds_op_witness_updates.operation_type as sbds_op_witness_updates_type,
            sbds_op_account_witness_votes.transaction_num as sbds_op_account_witness_votes_tx_num,
            sbds_op_account_witness_votes.operation_num as sbds_op_account_witness_votes_op_num,
            sbds_op_account_witness_votes.trx_id as sbds_op_account_witness_votes_trx_id,
            0 as sbds_op_account_witness_votes_virtual,
            sbds_op_account_witness_votes.operation_type as sbds_op_account_witness_votes_type,
            sbds_op_account_witness_proxies.transaction_num as sbds_op_account_witness_proxies_tx_num,
            sbds_op_account_witness_proxies.operation_num as sbds_op_account_witness_proxies_op_num,
            sbds_op_account_witness_proxies.trx_id as sbds_op_account_witness_proxies_trx_id,
            0 as sbds_op_account_witness_proxies_virtual,
            sbds_op_account_witness_proxies.operation_type as sbds_op_account_witness_proxies_type,
            sbds_op_customs.transaction_num as sbds_op_customs_tx_num,
            sbds_op_customs.operation_num as sbds_op_customs_op_num,
            sbds_op_customs.trx_id as sbds_op_customs_trx_id,
            0 as sbds_op_customs_virtual,
            sbds_op_customs.operation_type as sbds_op_customs_type,
            sbds_op_custom_jsons.transaction_num as sbds_op_custom_jsons_tx_num,
            sbds_op_custom_jsons.operation_num as sbds_op_custom_jsons_op_num,
            sbds_op_custom_jsons.trx_id as sbds_op_custom_jsons_trx_id,
            0 as sbds_op_custom_jsons_virtual,
            sbds_op_custom_jsons.operation_type as sbds_op_custom_jsons_type,
            sbds_op_custom_binaries.transaction_num as sbds_op_custom_binaries_tx_num,
            sbds_op_custom_binaries.operation_num as sbds_op_custom_binaries_op_num,
            sbds_op_custom_binaries.trx_id as sbds_op_custom_binaries_trx_id,
            0 as sbds_op_custom_binaries_virtual,
            sbds_op_custom_binaries.operation_type as sbds_op_custom_binaries_type,
            sbds_op_feed_publishes.transaction_num as sbds_op_feed_publishes_tx_num,
            sbds_op_feed_publishes.operation_num as sbds_op_feed_publishes_op_num,
            sbds_op_feed_publishes.trx_id as sbds_op_feed_publishes_trx_id,
            0 as sbds_op_feed_publishes_virtual,
            sbds_op_feed_publishes.operation_type as sbds_op_feed_publishes_type,
            sbds_op_converts.transaction_num as sbds_op_converts_tx_num,
            sbds_op_converts.operation_num as sbds_op_converts_op_num,
            sbds_op_converts.trx_id as sbds_op_converts_trx_id,
            0 as sbds_op_converts_virtual,
            sbds_op_converts.operation_type as sbds_op_converts_type,
            sbds_op_limit_order_creates.transaction_num as sbds_op_limit_order_creates_tx_num,
            sbds_op_limit_order_creates.operation_num as sbds_op_limit_order_creates_op_num,
            sbds_op_limit_order_creates.trx_id as sbds_op_limit_order_creates_trx_id,
            0 as sbds_op_limit_order_creates_virtual,
            sbds_op_limit_order_creates.operation_type as sbds_op_limit_order_creates_type,
            sbds_op_limit_order_create2s.transaction_num as sbds_op_limit_order_create2s_tx_num,
            sbds_op_limit_order_create2s.operation_num as sbds_op_limit_order_create2s_op_num,
            sbds_op_limit_order_create2s.trx_id as sbds_op_limit_order_create2s_trx_id,
            0 as sbds_op_limit_order_create2s_virtual,
            sbds_op_limit_order_create2s.operation_type as sbds_op_limit_order_create2s_type,
            sbds_op_limit_order_cancels.transaction_num as sbds_op_limit_order_cancels_tx_num,
            sbds_op_limit_order_cancels.operation_num as sbds_op_limit_order_cancels_op_num,
            sbds_op_limit_order_cancels.trx_id as sbds_op_limit_order_cancels_trx_id,
            0 as sbds_op_limit_order_cancels_virtual,
            sbds_op_limit_order_cancels.operation_type as sbds_op_limit_order_cancels_type,
            sbds_op_pows.transaction_num as sbds_op_pows_tx_num,
            sbds_op_pows.operation_num as sbds_op_pows_op_num,
            sbds_op_pows.trx_id as sbds_op_pows_trx_id,
            0 as sbds_op_pows_virtual,
            sbds_op_pows.operation_type as sbds_op_pows_type,
            sbds_op_pow2s.transaction_num as sbds_op_pow2s_tx_num,
            sbds_op_pow2s.operation_num as sbds_op_pow2s_op_num,
            sbds_op_pow2s.trx_id as sbds_op_pow2s_trx_id,
            0 as sbds_op_pow2s_virtual,
            sbds_op_pow2s.operation_type as sbds_op_pow2s_type,
            sbds_op_report_over_productions.transaction_num as sbds_op_report_over_productions_tx_num,
            sbds_op_report_over_productions.operation_num as sbds_op_report_over_productions_op_num,
            sbds_op_report_over_productions.trx_id as sbds_op_report_over_productions_trx_id,
            0 as sbds_op_report_over_productions_virtual,
            sbds_op_report_over_productions.operation_type as sbds_op_report_over_productions_type,
            sbds_op_request_account_recoveries.transaction_num as sbds_op_request_account_recoveries_tx_num,
            sbds_op_request_account_recoveries.operation_num as sbds_op_request_account_recoveries_op_num,
            sbds_op_request_account_recoveries.trx_id as sbds_op_request_account_recoveries_trx_id,
            0 as sbds_op_request_account_recoveries_virtual,
            sbds_op_request_account_recoveries.operation_type as sbds_op_request_account_recoveries_type,
            sbds_op_recover_accounts.transaction_num as sbds_op_recover_accounts_tx_num,
            sbds_op_recover_accounts.operation_num as sbds_op_recover_accounts_op_num,
            sbds_op_recover_accounts.trx_id as sbds_op_recover_accounts_trx_id,
            0 as sbds_op_recover_accounts_virtual,
            sbds_op_recover_accounts.operation_type as sbds_op_recover_accounts_type,
            sbds_op_reset_accounts.transaction_num as sbds_op_reset_accounts_tx_num,
            sbds_op_reset_accounts.operation_num as sbds_op_reset_accounts_op_num,
            sbds_op_reset_accounts.trx_id as sbds_op_reset_accounts_trx_id,
            0 as sbds_op_reset_accounts_virtual,
            sbds_op_reset_accounts.operation_type as sbds_op_reset_accounts_type,
            sbds_op_set_reset_accounts.transaction_num as sbds_op_set_reset_accounts_tx_num,
            sbds_op_set_reset_accounts.operation_num as sbds_op_set_reset_accounts_op_num,
            sbds_op_set_reset_accounts.trx_id as sbds_op_set_reset_accounts_trx_id,
            0 as sbds_op_set_reset_accounts_virtual,
            sbds_op_set_reset_accounts.operation_type as sbds_op_set_reset_accounts_type,
            sbds_op_change_recovery_accounts.transaction_num as sbds_op_change_recovery_accounts_tx_num,
            sbds_op_change_recovery_accounts.operation_num as sbds_op_change_recovery_accounts_op_num,
            sbds_op_change_recovery_accounts.trx_id as sbds_op_change_recovery_accounts_trx_id,
            0 as sbds_op_change_recovery_accounts_virtual,
            sbds_op_change_recovery_accounts.operation_type as sbds_op_change_recovery_accounts_type,
            sbds_op_transfer_to_saving.transaction_num as sbds_op_transfer_to_saving_tx_num,
            sbds_op_transfer_to_saving.operation_num as sbds_op_transfer_to_saving_op_num,
            sbds_op_transfer_to_saving.trx_id as sbds_op_transfer_to_saving_trx_id,
            0 as sbds_op_transfer_to_saving_virtual,
            sbds_op_transfer_to_saving.operation_type as sbds_op_transfer_to_saving_type,
            sbds_op_transfer_from_saving.transaction_num as sbds_op_transfer_from_saving_tx_num,
            sbds_op_transfer_from_saving.operation_num as sbds_op_transfer_from_saving_op_num,
            sbds_op_transfer_from_saving.trx_id as sbds_op_transfer_from_saving_trx_id,
            0 as sbds_op_transfer_from_saving_virtual,
            sbds_op_transfer_from_saving.operation_type as sbds_op_transfer_from_saving_type,
            sbds_op_cancel_transfer_from_saving.transaction_num as sbds_op_cancel_transfer_from_saving_tx_num,
            sbds_op_cancel_transfer_from_saving.operation_num as sbds_op_cancel_transfer_from_saving_op_num,
            sbds_op_cancel_transfer_from_saving.trx_id as sbds_op_cancel_transfer_from_saving_trx_id,
            0 as sbds_op_cancel_transfer_from_saving_virtual,
            sbds_op_cancel_transfer_from_saving.operation_type as sbds_op_cancel_transfer_from_saving_type,
            sbds_op_decline_voting_right.transaction_num as sbds_op_decline_voting_right_tx_num,
            sbds_op_decline_voting_right.operation_num as sbds_op_decline_voting_right_op_num,
            sbds_op_decline_voting_right.trx_id as sbds_op_decline_voting_right_trx_id,
            0 as sbds_op_decline_voting_right_virtual,
            sbds_op_decline_voting_right.operation_type as sbds_op_decline_voting_right_type,
            sbds_op_claim_reward_balances.transaction_num as sbds_op_claim_reward_balances_tx_num,
            sbds_op_claim_reward_balances.operation_num as sbds_op_claim_reward_balances_op_num,
            sbds_op_claim_reward_balances.trx_id as sbds_op_claim_reward_balances_trx_id,
            0 as sbds_op_claim_reward_balances_virtual,
            sbds_op_claim_reward_balances.operation_type as sbds_op_claim_reward_balances_type,
            sbds_op_delegate_vesting_share.transaction_num as sbds_op_delegate_vesting_share_tx_num,
            sbds_op_delegate_vesting_share.operation_num as sbds_op_delegate_vesting_share_op_num,
            sbds_op_delegate_vesting_share.trx_id as sbds_op_delegate_vesting_share_trx_id,
            0 as sbds_op_delegate_vesting_share_virtual,
            sbds_op_delegate_vesting_share.operation_type as sbds_op_delegate_vesting_share_type,
            sbds_op_virtual_author_rewards.transaction_num as sbds_op_virtual_author_rewards_tx_num,
            sbds_op_virtual_author_rewards.operation_num as sbds_op_virtual_author_rewards_op_num,
            sbds_op_virtual_author_rewards.id as sbds_op_virtual_author_rewards_trx_id,
             1 as sbds_op_virtual_author_rewards_virtual,
            sbds_op_virtual_author_rewards.operation_type as sbds_op_virtual_author_rewards_type,
            sbds_op_virtual_curation_rewards.transaction_num as sbds_op_virtual_curation_rewards_tx_num,
            sbds_op_virtual_curation_rewards.operation_num as sbds_op_virtual_curation_rewards_op_num,
            sbds_op_virtual_curation_rewards.id as sbds_op_virtual_curation_rewards_trx_id,
             1 as sbds_op_virtual_curation_rewards_virtual,
            sbds_op_virtual_curation_rewards.operation_type as sbds_op_virtual_curation_rewards_type,
            sbds_op_virtual_comment_rewards.transaction_num as sbds_op_virtual_comment_rewards_tx_num,
            sbds_op_virtual_comment_rewards.operation_num as sbds_op_virtual_comment_rewards_op_num,
            sbds_op_virtual_comment_rewards.id as sbds_op_virtual_comment_rewards_trx_id,
             1 as sbds_op_virtual_comment_rewards_virtual,
            sbds_op_virtual_comment_rewards.operation_type as sbds_op_virtual_comment_rewards_type,
            sbds_op_virtual_liquidity_rewards.transaction_num as sbds_op_virtual_liquidity_rewards_tx_num,
            sbds_op_virtual_liquidity_rewards.operation_num as sbds_op_virtual_liquidity_rewards_op_num,
            sbds_op_virtual_liquidity_rewards.id as sbds_op_virtual_liquidity_rewards_trx_id,
             1 as sbds_op_virtual_liquidity_rewards_virtual,
            sbds_op_virtual_liquidity_rewards.operation_type as sbds_op_virtual_liquidity_rewards_type,
            sbds_op_virtual_interests.transaction_num as sbds_op_virtual_interests_tx_num,
            sbds_op_virtual_interests.operation_num as sbds_op_virtual_interests_op_num,
            sbds_op_virtual_interests.id as sbds_op_virtual_interests_trx_id,
             1 as sbds_op_virtual_interests_virtual,
            sbds_op_virtual_interests.operation_type as sbds_op_virtual_interests_type,
            sbds_op_virtual_fill_convert_requests.transaction_num as sbds_op_virtual_fill_convert_requests_tx_num,
            sbds_op_virtual_fill_convert_requests.operation_num as sbds_op_virtual_fill_convert_requests_op_num,
            sbds_op_virtual_fill_convert_requests.id as sbds_op_virtual_fill_convert_requests_trx_id,
             1 as sbds_op_virtual_fill_convert_requests_virtual,
            sbds_op_virtual_fill_convert_requests.operation_type as sbds_op_virtual_fill_convert_requests_type,
            sbds_op_virtual_fill_vesting_withdraws.transaction_num as sbds_op_virtual_fill_vesting_withdraws_tx_num,
            sbds_op_virtual_fill_vesting_withdraws.operation_num as sbds_op_virtual_fill_vesting_withdraws_op_num,
            sbds_op_virtual_fill_vesting_withdraws.id as sbds_op_virtual_fill_vesting_withdraws_trx_id,
             1 as sbds_op_virtual_fill_vesting_withdraws_virtual,
            sbds_op_virtual_fill_vesting_withdraws.operation_type as sbds_op_virtual_fill_vesting_withdraws_type,
            sbds_op_virtual_shutdown_witnesses.transaction_num as sbds_op_virtual_shutdown_witnesses_tx_num,
            sbds_op_virtual_shutdown_witnesses.operation_num as sbds_op_virtual_shutdown_witnesses_op_num,
            sbds_op_virtual_shutdown_witnesses.id as sbds_op_virtual_shutdown_witnesses_trx_id,
             1 as sbds_op_virtual_shutdown_witnesses_virtual,
            sbds_op_virtual_shutdown_witnesses.operation_type as sbds_op_virtual_shutdown_witnesses_type,
            sbds_op_virtual_fill_orders.transaction_num as sbds_op_virtual_fill_orders_tx_num,
            sbds_op_virtual_fill_orders.operation_num as sbds_op_virtual_fill_orders_op_num,
            sbds_op_virtual_fill_orders.id as sbds_op_virtual_fill_orders_trx_id,
             1 as sbds_op_virtual_fill_orders_virtual,
            sbds_op_virtual_fill_orders.operation_type as sbds_op_virtual_fill_orders_type,
            sbds_op_virtual_fill_transfer_from_saving.transaction_num as sbds_op_virtual_fill_transfer_from_saving_tx_num,
            sbds_op_virtual_fill_transfer_from_saving.operation_num as sbds_op_virtual_fill_transfer_from_saving_op_num,
            sbds_op_virtual_fill_transfer_from_saving.id as sbds_op_virtual_fill_transfer_from_saving_trx_id,
             1 as sbds_op_virtual_fill_transfer_from_saving_virtual,
            sbds_op_virtual_fill_transfer_from_saving.operation_type as sbds_op_virtual_fill_transfer_from_saving_type,
            sbds_op_virtual_hardforks.transaction_num as sbds_op_virtual_hardforks_tx_num,
            sbds_op_virtual_hardforks.operation_num as sbds_op_virtual_hardforks_op_num,
            sbds_op_virtual_hardforks.id as sbds_op_virtual_hardforks_trx_id,
             1 as sbds_op_virtual_hardforks_virtual,
            sbds_op_virtual_hardforks.operation_type as sbds_op_virtual_hardforks_type,
            sbds_op_virtual_comment_payout_updates.transaction_num as sbds_op_virtual_comment_payout_updates_tx_num,
            sbds_op_virtual_comment_payout_updates.operation_num as sbds_op_virtual_comment_payout_updates_op_num,
            sbds_op_virtual_comment_payout_updates.id as sbds_op_virtual_comment_payout_updates_trx_id,
             1 as sbds_op_virtual_comment_payout_updates_virtual,
            sbds_op_virtual_comment_payout_updates.operation_type as sbds_op_virtual_comment_payout_updates_type,
            sbds_op_virtual_return_vesting_delegations.transaction_num as sbds_op_virtual_return_vesting_delegations_tx_num,
            sbds_op_virtual_return_vesting_delegations.operation_num as sbds_op_virtual_return_vesting_delegations_op_num,
            sbds_op_virtual_return_vesting_delegations.id as sbds_op_virtual_return_vesting_delegations_trx_id,
             1 as sbds_op_virtual_return_vesting_delegations_virtual,
            sbds_op_virtual_return_vesting_delegations.operation_type as sbds_op_virtual_return_vesting_delegations_type,
            sbds_op_virtual_comment_benefactor_rewards.transaction_num as sbds_op_virtual_comment_benefactor_rewards_tx_num,
            sbds_op_virtual_comment_benefactor_rewards.operation_num as sbds_op_virtual_comment_benefactor_rewards_op_num,
            sbds_op_virtual_comment_benefactor_rewards.id as sbds_op_virtual_comment_benefactor_rewards_trx_id,
             1 as sbds_op_virtual_comment_benefactor_rewards_virtual,
            sbds_op_virtual_comment_benefactor_rewards.operation_type as sbds_op_virtual_comment_benefactor_rewards_type,
            sbds_op_virtual_producer_rewards.transaction_num as sbds_op_virtual_producer_rewards_tx_num,
            sbds_op_virtual_producer_rewards.operation_num as sbds_op_virtual_producer_rewards_op_num,
            sbds_op_virtual_producer_rewards.id as sbds_op_virtual_producer_rewards_trx_id,
             1 as sbds_op_virtual_producer_rewards_virtual,
            sbds_op_virtual_producer_rewards.operation_type as sbds_op_virtual_producer_rewards_typeFROM sbds_core_blocks
    JOIN sbds_op_account_creates USING(block_num)
    JOIN sbds_op_account_create_with_delegations USING(block_num)
    JOIN sbds_op_account_updates USING(block_num)
    JOIN sbds_op_comments USING(block_num)
    JOIN sbds_op_comment_option USING(block_num)
    JOIN sbds_op_challenge_authorities USING(block_num)
    JOIN sbds_op_prove_authorities USING(block_num)
    JOIN sbds_op_delete_comments USING(block_num)
    JOIN sbds_op_votes USING(block_num)
    JOIN sbds_op_transfers USING(block_num)
    JOIN sbds_op_escrow_transfers USING(block_num)
    JOIN sbds_op_escrow_approves USING(block_num)
    JOIN sbds_op_escrow_disputes USING(block_num)
    JOIN sbds_op_escrow_releases USING(block_num)
    JOIN sbds_op_transfer_to_vestings USING(block_num)
    JOIN sbds_op_withdraw_vestings USING(block_num)
    JOIN sbds_op_set_withdraw_vesting_routes USING(block_num)
    JOIN sbds_op_witness_updates USING(block_num)
    JOIN sbds_op_account_witness_votes USING(block_num)
    JOIN sbds_op_account_witness_proxies USING(block_num)
    JOIN sbds_op_customs USING(block_num)
    JOIN sbds_op_custom_jsons USING(block_num)
    JOIN sbds_op_custom_binaries USING(block_num)
    JOIN sbds_op_feed_publishes USING(block_num)
    JOIN sbds_op_converts USING(block_num)
    JOIN sbds_op_limit_order_creates USING(block_num)
    JOIN sbds_op_limit_order_create2s USING(block_num)
    JOIN sbds_op_limit_order_cancels USING(block_num)
    JOIN sbds_op_pows USING(block_num)
    JOIN sbds_op_pow2s USING(block_num)
    JOIN sbds_op_report_over_productions USING(block_num)
    JOIN sbds_op_request_account_recoveries USING(block_num)
    JOIN sbds_op_recover_accounts USING(block_num)
    JOIN sbds_op_reset_accounts USING(block_num)
    JOIN sbds_op_set_reset_accounts USING(block_num)
    JOIN sbds_op_change_recovery_accounts USING(block_num)
    JOIN sbds_op_transfer_to_saving USING(block_num)
    JOIN sbds_op_transfer_from_saving USING(block_num)
    JOIN sbds_op_cancel_transfer_from_saving USING(block_num)
    JOIN sbds_op_decline_voting_right USING(block_num)
    JOIN sbds_op_claim_reward_balances USING(block_num)
    JOIN sbds_op_delegate_vesting_share USING(block_num)
    JOIN sbds_op_virtual_author_rewards USING(block_num)
    JOIN sbds_op_virtual_curation_rewards USING(block_num)
    JOIN sbds_op_virtual_comment_rewards USING(block_num)
    JOIN sbds_op_virtual_liquidity_rewards USING(block_num)
    JOIN sbds_op_virtual_interests USING(block_num)
    JOIN sbds_op_virtual_fill_convert_requests USING(block_num)
    JOIN sbds_op_virtual_fill_vesting_withdraws USING(block_num)
    JOIN sbds_op_virtual_shutdown_witnesses USING(block_num)
    JOIN sbds_op_virtual_fill_orders USING(block_num)
    JOIN sbds_op_virtual_fill_transfer_from_saving USING(block_num)
    JOIN sbds_op_virtual_hardforks USING(block_num)
    JOIN sbds_op_virtual_comment_payout_updates USING(block_num)
    JOIN sbds_op_virtual_return_vesting_delegations USING(block_num)
    JOIN sbds_op_virtual_comment_benefactor_rewards USING(block_num)
    JOIN sbds_op_virtual_producer_rewards USING(block_num)
    ;
'''


def create_operations_view():
    from sbds.storages.db.tables import metadata
    operations_view = view('sbds_views_operations', metadata, OPERATIONS_SELECT_SQL)


create_operations_view()
