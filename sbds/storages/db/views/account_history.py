# -*- coding: utf-8 -*-
from .views import view

'''
    Relevant Source Code
    --------------------
    https://github.com/steemit/steem/blob/v0.19.4rc1/libraries/plugins/apis/account_history_api/include/steem/plugins/account_history_api/account_history_api.hpp

    struct api_operation_object
    {
       api_operation_object() {}
       api_operation_object( const steem::chain::operation_object& op_obj ) :
          trx_id( op_obj.trx_id ),
          block( op_obj.block ),
          trx_in_block( op_obj.trx_in_block ),
          virtual_op( op_obj.virtual_op ),
          timestamp( op_obj.timestamp )
       {
          op = fc::raw::unpack_from_buffer< steem::protocol::operation >( op_obj.serialized_op );
       }

       steem::protocol::transaction_id_type trx_id;
       uint32_t                               block = 0;
       uint32_t                               trx_in_block = 0;
       uint16_t                               op_in_trx = 0;
       uint64_t                               virtual_op = 0;
       fc::time_point_sec                     timestamp;
       steem::protocol::operation             op;
    };



    struct get_account_history_args
    {
       steem::protocol::account_name_type   account;
       uint64_t                               start = -1;
       uint32_t                               limit = 1000;
    };

    struct get_account_history_return
    {
       std::map< uint32_t, api_operation_object > history;
    };




    Example API Response
    ----------------
    [
            967,
            {
                "block": 20334455,
                "op": [
                    "author_reward",
                    {
                        "author": "layz3r",
                        "permlink": "google-knowledge-graph-groks-peps",
                        "sbd_payout": "0.634 SBD",
                        "steem_payout": "0.000 STEEM",
                        "vesting_payout": "396.311842 VESTS"
                    }
                ],
                "op_in_trx": 1,
                "timestamp": "2018-03-02T22:13:21",
                "trx_id": "0000000000000000000000000000000000000000",
                "trx_in_block": 60,
                "virtual_op": 0
            }
        ]
    ]

'''


ALL_OPERATIONS_SQL = '''
    CREATE VIEW sbds_all_ops_view AS
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_account_creates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_account_create_with_delegations
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_account_updates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_comments
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_comment_option
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_challenge_authorities
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_prove_authorities
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_delete_comments
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_votes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_transfers
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_escrow_transfers
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_escrow_approves
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_escrow_disputes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_escrow_releases
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_transfer_to_vestings
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_withdraw_vestings
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_set_withdraw_vesting_routes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_witness_updates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_account_witness_votes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_account_witness_proxies
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_customs
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_custom_jsons
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_custom_binaries
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_feed_publishes
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_converts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_limit_order_creates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_limit_order_create2s
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_limit_order_cancels
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_pows
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_report_over_productions
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_request_account_recoveries
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_recover_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_reset_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_set_reset_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_change_recovery_accounts
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_transfer_to_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_transfer_from_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_cancel_transfer_from_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_decline_voting_right
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_claim_reward_balances
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_delegate_vesting_share
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_author_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_curation_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_comment_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_liquidity_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_interests
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_fill_convert_requests
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_fill_vesting_withdraws
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_shutdown_witnesses
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_fill_orders
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_fill_transfer_from_saving
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_comment_payout_updates
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_return_vesting_delegations
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_comment_benefactor_rewards
    UNION ALL
    SELECT
        block_num,
        transaction_num,
        operation_num,
        operation_type,
        accounts,
        raw
    FROM sbds_op_virtual_producer_rewards

    '''
