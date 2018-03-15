# -*- coding: utf-8 -*-
from .views import view


def create_accounts_view():
    from sbds.storages.db.tables import metadata
    accounts_view = view('sbds_views_accounts',metadata, '''
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'creator' as field0_name,
        sbds_op_account_creates.creator as field0_value,
        'new_account_name' as field1_name,
        sbds_op_account_creates.new_account_name as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_account_creates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'creator' as field0_name,
        sbds_op_account_create_with_delegations.creator as field0_value,
        'new_account_name' as field1_name,
        sbds_op_account_create_with_delegations.new_account_name as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_account_create_with_delegations
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_account_updates.account as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_account_updates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'parent_author' as field0_name,
        sbds_op_comments.parent_author as field0_value,
        'author' as field1_name,
        sbds_op_comments.author as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_comments
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'author' as field0_name,
        sbds_op_comment_option.author as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_comment_option
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'challenger' as field0_name,
        sbds_op_challenge_authorities.challenger as field0_value,
        'challenged' as field1_name,
        sbds_op_challenge_authorities.challenged as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_challenge_authorities
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'challenged' as field0_name,
        sbds_op_prove_authorities.challenged as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_prove_authorities
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'author' as field0_name,
        sbds_op_delete_comments.author as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_delete_comments
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'voter' as field0_name,
        sbds_op_votes.voter as field0_value,
        'author' as field1_name,
        sbds_op_votes.author as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_votes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_transfers.from as field0_value,
        'to' as field1_name,
        sbds_op_transfers.to as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_transfers
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_escrow_transfers.from as field0_value,
        'to' as field1_name,
        sbds_op_escrow_transfers.to as field1_value,
        'agent' as field2_name,
        sbds_op_escrow_transfers.agent as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_escrow_transfers
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_escrow_approves.from as field0_value,
        'to' as field1_name,
        sbds_op_escrow_approves.to as field1_value,
        'agent' as field2_name,
        sbds_op_escrow_approves.agent as field2_value,
        'who' as field3_name,
        sbds_op_escrow_approves.who as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_escrow_approves
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_escrow_disputes.from as field0_value,
        'to' as field1_name,
        sbds_op_escrow_disputes.to as field1_value,
        'agent' as field2_name,
        sbds_op_escrow_disputes.agent as field2_value,
        'who' as field3_name,
        sbds_op_escrow_disputes.who as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_escrow_disputes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_escrow_releases.from as field0_value,
        'to' as field1_name,
        sbds_op_escrow_releases.to as field1_value,
        'agent' as field2_name,
        sbds_op_escrow_releases.agent as field2_value,
        'who' as field3_name,
        sbds_op_escrow_releases.who as field3_value,
        'receiver' as field4_name,
        sbds_op_escrow_releases.receiver as field4_value
        FROM sbds_op_escrow_releases
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_transfer_to_vestings.from as field0_value,
        'to' as field1_name,
        sbds_op_transfer_to_vestings.to as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_transfer_to_vestings
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_withdraw_vestings.account as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_withdraw_vestings
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from_account' as field0_name,
        sbds_op_set_withdraw_vesting_routes.from_account as field0_value,
        'to_account' as field1_name,
        sbds_op_set_withdraw_vesting_routes.to_account as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_set_withdraw_vesting_routes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_witness_updates.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_witness_updates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_account_witness_votes.account as field0_value,
        'witness' as field1_name,
        sbds_op_account_witness_votes.witness as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_account_witness_votes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_account_witness_proxies.account as field0_value,
        'proxy' as field1_name,
        sbds_op_account_witness_proxies.proxy as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_account_witness_proxies
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'publisher' as field0_name,
        sbds_op_feed_publishes.publisher as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_feed_publishes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_converts.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_converts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_limit_order_creates.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_limit_order_creates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_limit_order_create2s.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_limit_order_create2s
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_limit_order_cancels.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_limit_order_cancels
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'worker_account' as field0_name,
        sbds_op_pows.worker_account as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_pows
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'reporter' as field0_name,
        sbds_op_report_over_productions.reporter as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_report_over_productions
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'recovery_account' as field0_name,
        sbds_op_request_account_recoveries.recovery_account as field0_value,
        'account_to_recover' as field1_name,
        sbds_op_request_account_recoveries.account_to_recover as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_request_account_recoveries
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account_to_recover' as field0_name,
        sbds_op_recover_accounts.account_to_recover as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_recover_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'reset_account' as field0_name,
        sbds_op_reset_accounts.reset_account as field0_value,
        'account_to_reset' as field1_name,
        sbds_op_reset_accounts.account_to_reset as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_reset_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_set_reset_accounts.account as field0_value,
        'current_reset_account' as field1_name,
        sbds_op_set_reset_accounts.current_reset_account as field1_value,
        'reset_account' as field2_name,
        sbds_op_set_reset_accounts.reset_account as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_set_reset_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account_to_recover' as field0_name,
        sbds_op_change_recovery_accounts.account_to_recover as field0_value,
        'new_recovery_account' as field1_name,
        sbds_op_change_recovery_accounts.new_recovery_account as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_change_recovery_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_transfer_to_saving.from as field0_value,
        'to' as field1_name,
        sbds_op_transfer_to_saving.to as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_transfer_to_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_transfer_from_saving.from as field0_value,
        'to' as field1_name,
        sbds_op_transfer_from_saving.to as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_transfer_from_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_cancel_transfer_from_saving.from as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_cancel_transfer_from_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_decline_voting_right.account as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_decline_voting_right
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_claim_reward_balances.account as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_claim_reward_balances
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'delegator' as field0_name,
        sbds_op_delegate_vesting_share.delegator as field0_value,
        'delegatee' as field1_name,
        sbds_op_delegate_vesting_share.delegatee as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_delegate_vesting_share
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'author' as field0_name,
        sbds_op_virtual_author_rewards.author as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_author_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'curator' as field0_name,
        sbds_op_virtual_curation_rewards.curator as field0_value,
        'comment_author' as field1_name,
        sbds_op_virtual_curation_rewards.comment_author as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_curation_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'author' as field0_name,
        sbds_op_virtual_comment_rewards.author as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_comment_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_virtual_liquidity_rewards.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_liquidity_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_virtual_interests.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_interests
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_virtual_fill_convert_requests.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_fill_convert_requests
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from_account' as field0_name,
        sbds_op_virtual_fill_vesting_withdraws.from_account as field0_value,
        'to_account' as field1_name,
        sbds_op_virtual_fill_vesting_withdraws.to_account as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_fill_vesting_withdraws
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'owner' as field0_name,
        sbds_op_virtual_shutdown_witnesses.owner as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_shutdown_witnesses
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'current_owner' as field0_name,
        sbds_op_virtual_fill_orders.current_owner as field0_value,
        'open_owner' as field1_name,
        sbds_op_virtual_fill_orders.open_owner as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_fill_orders
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'from' as field0_name,
        sbds_op_virtual_fill_transfer_from_saving.from as field0_value,
        'to' as field1_name,
        sbds_op_virtual_fill_transfer_from_saving.to as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_fill_transfer_from_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'author' as field0_name,
        sbds_op_virtual_comment_payout_updates.author as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_comment_payout_updates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'account' as field0_name,
        sbds_op_virtual_return_vesting_delegations.account as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_return_vesting_delegations
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'benefactor' as field0_name,
        sbds_op_virtual_comment_benefactor_rewards.benefactor as field0_value,
        'author' as field1_name,
        sbds_op_virtual_comment_benefactor_rewards.author as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_comment_benefactor_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        trx_id,
        'producer' as field0_name,
        sbds_op_virtual_producer_rewards.producer as field0_value,
        null as field1_name,
        null as field1_value,
        null as field2_name,
        null as field2_value,
        null as field3_name,
        null as field3_value,
        null as field4_name,
        null as field4_value
        FROM sbds_op_virtual_producer_rewards
    
    ORDER BY block_num ASC, transaction_num ASC, operation_num ASC;
    ''')

create_accounts_view()

