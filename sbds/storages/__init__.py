# -*- coding: utf-8 -*-
from collections import namedtuple

import sbds.logging

logger = sbds.logging.getLogger(__name__)

'''
block
=====
{
  "previous": "000b89c1773f64b2c16f5d3103caeac614c34d7b",
  "timestamp": "2016-04-20T10:10:06",
  "witness": "frelia",
  "transaction_merkle_root": "0000000000000000000000000000000000000000",
  "extensions": [],
  "witness_signature": "1f01cbfd9fa606c782bd5df8e6201b6dd704044815c9e8ae88f7f945774be0d9800253e01e7d0fbe4b6c37e1ac75ac5d5f768609663ededc98064d7266b523a41f",
  "transactions": []
}
'''

Block = namedtuple('Block', ['previous',
                             'timestamp',
                             'witness',
                             'transaction_merkle_root',
                             'extentions',
                             'witness_signature',
                             'transactions'])


class AbstractStorageContainer(object):
    def __init__(self, **kwargs):
        pass

    def __iter__(self):
        raise NotImplementedError

    def __reversed__(self):
        raise NotImplementedError

    def __contains__(self, item):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __eq__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def add(self, item):
        raise NotImplementedError

    def add_many(self, items):
        raise NotImplementedError


'''
transaction
==================
{
    "expiration": "2016-12-19T17:11:21",
    "extensions": [],
    "operations": [
        ["vote", {
            "voter": "intelliguy",
            "author": "trevor.george",
            "weight": 10000,
            "permlink": "what-is-it-about-steemit-that-sets-it-apart-from-other-blogging-platforms"}
        ]
    ],
    "signatures": [
        "20650caa0464a35f83e7a1a7e5ce28914eb179dd4edada3650f6ca5df16d0d2d9160c61c62c22ccf43a780ed90ababf1fb49bffdb0d095024e2a27b2c3549ff553"
    ],
    "ref_block_num": 59862,
    "ref_block_prefix": 4197255167
}
'''

Transaction = namedtuple('Transaction', ['expiration',
                                         'extensions',
                                         'operations',
                                         'signatures',
                                         'ref_block_num',
                                         'ref_block_prefix'])

used_operation_types = frozenset([
    'account_create',
    'account_update',
    'account_witness_proxy',
    'account_witness_vote',
    'cancel_transfer_from_savings',
    'change_recovery_account',
    'comment',
    'comment_options',
    'convert',
    'custom',
    'custom_json',
    'delete_comment',
    'feed_publish',
    'limit_order_cancel',
    'limit_order_create',
    'pow',
    'pow2',
    'recover_account',
    'request_account_recovery',
    'set_withdraw_vesting_route',
    'transfer',
    'transfer_from_savings',
    'transfer_to_savings',
    'transfer_to_vesting',
    'vote',
    'withdraw_vesting',
    'witness_update'
])

unused_operation_types = frozenset([
    'challenge_authority',
    'custom_binary_operation',
    'decline_voting_rights_operation',
    'escrow_approve',
    'escrow_dispute',
    'escrow_release',
    'escrow_transfer',
    'limit_order_create2',
    'prove_authority',
    'report_over_production',
    'reset_account_operation',
    'set_reset_account_operation'
])

operation_types = used_operation_types.union(unused_operation_types)
