# -*- coding: utf-8 -*-
from .views import view


COUNT_OPERATIONS_SELECT_SQL = '''
    
        SELECT 'sbds_op_account_creates' AS operation_type, COUNT(*) AS count FROM sbds_op_account_creates GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_account_create_with_delegations' AS operation_type, COUNT(*) AS count FROM sbds_op_account_create_with_delegations GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_account_updates' AS operation_type, COUNT(*) AS count FROM sbds_op_account_updates GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_comments' AS operation_type, COUNT(*) AS count FROM sbds_op_comments GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_comment_option' AS operation_type, COUNT(*) AS count FROM sbds_op_comment_option GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_challenge_authorities' AS operation_type, COUNT(*) AS count FROM sbds_op_challenge_authorities GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_prove_authorities' AS operation_type, COUNT(*) AS count FROM sbds_op_prove_authorities GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_delete_comments' AS operation_type, COUNT(*) AS count FROM sbds_op_delete_comments GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_votes' AS operation_type, COUNT(*) AS count FROM sbds_op_votes GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_transfers' AS operation_type, COUNT(*) AS count FROM sbds_op_transfers GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_escrow_transfers' AS operation_type, COUNT(*) AS count FROM sbds_op_escrow_transfers GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_escrow_approves' AS operation_type, COUNT(*) AS count FROM sbds_op_escrow_approves GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_escrow_disputes' AS operation_type, COUNT(*) AS count FROM sbds_op_escrow_disputes GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_escrow_releases' AS operation_type, COUNT(*) AS count FROM sbds_op_escrow_releases GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_transfer_to_vestings' AS operation_type, COUNT(*) AS count FROM sbds_op_transfer_to_vestings GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_withdraw_vestings' AS operation_type, COUNT(*) AS count FROM sbds_op_withdraw_vestings GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_set_withdraw_vesting_routes' AS operation_type, COUNT(*) AS count FROM sbds_op_set_withdraw_vesting_routes GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_witness_updates' AS operation_type, COUNT(*) AS count FROM sbds_op_witness_updates GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_account_witness_votes' AS operation_type, COUNT(*) AS count FROM sbds_op_account_witness_votes GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_account_witness_proxies' AS operation_type, COUNT(*) AS count FROM sbds_op_account_witness_proxies GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_customs' AS operation_type, COUNT(*) AS count FROM sbds_op_customs GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_custom_jsons' AS operation_type, COUNT(*) AS count FROM sbds_op_custom_jsons GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_custom_binaries' AS operation_type, COUNT(*) AS count FROM sbds_op_custom_binaries GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_feed_publishes' AS operation_type, COUNT(*) AS count FROM sbds_op_feed_publishes GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_converts' AS operation_type, COUNT(*) AS count FROM sbds_op_converts GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_limit_order_creates' AS operation_type, COUNT(*) AS count FROM sbds_op_limit_order_creates GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_limit_order_create2s' AS operation_type, COUNT(*) AS count FROM sbds_op_limit_order_create2s GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_limit_order_cancels' AS operation_type, COUNT(*) AS count FROM sbds_op_limit_order_cancels GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_pows' AS operation_type, COUNT(*) AS count FROM sbds_op_pows GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_pow2s' AS operation_type, COUNT(*) AS count FROM sbds_op_pow2s GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_report_over_productions' AS operation_type, COUNT(*) AS count FROM sbds_op_report_over_productions GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_request_account_recoveries' AS operation_type, COUNT(*) AS count FROM sbds_op_request_account_recoveries GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_recover_accounts' AS operation_type, COUNT(*) AS count FROM sbds_op_recover_accounts GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_reset_accounts' AS operation_type, COUNT(*) AS count FROM sbds_op_reset_accounts GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_set_reset_accounts' AS operation_type, COUNT(*) AS count FROM sbds_op_set_reset_accounts GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_change_recovery_accounts' AS operation_type, COUNT(*) AS count FROM sbds_op_change_recovery_accounts GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_transfer_to_saving' AS operation_type, COUNT(*) AS count FROM sbds_op_transfer_to_saving GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_transfer_from_saving' AS operation_type, COUNT(*) AS count FROM sbds_op_transfer_from_saving GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_cancel_transfer_from_saving' AS operation_type, COUNT(*) AS count FROM sbds_op_cancel_transfer_from_saving GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_decline_voting_right' AS operation_type, COUNT(*) AS count FROM sbds_op_decline_voting_right GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_claim_reward_balances' AS operation_type, COUNT(*) AS count FROM sbds_op_claim_reward_balances GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_delegate_vesting_share' AS operation_type, COUNT(*) AS count FROM sbds_op_delegate_vesting_share GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_author_rewards' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_author_rewards GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_curation_rewards' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_curation_rewards GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_comment_rewards' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_comment_rewards GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_liquidity_rewards' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_liquidity_rewards GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_interests' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_interests GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_fill_convert_requests' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_fill_convert_requests GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_fill_vesting_withdraws' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_fill_vesting_withdraws GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_shutdown_witnesses' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_shutdown_witnesses GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_fill_orders' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_fill_orders GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_fill_transfer_from_saving' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_fill_transfer_from_saving GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_hardforks' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_hardforks GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_comment_payout_updates' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_comment_payout_updates GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_return_vesting_delegations' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_return_vesting_delegations GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_comment_benefactor_rewards' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_comment_benefactor_rewards GROUP BY operation_type
    UNION ALL
        SELECT 'sbds_op_virtual_producer_rewards' AS operation_type, COUNT(*) AS count FROM sbds_op_virtual_producer_rewards GROUP BY operation_type
    ;
'''


