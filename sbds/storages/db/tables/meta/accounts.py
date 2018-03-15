# -*- coding: utf-8 -*-
import itertools as it

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship

from sbds.storages.db.tables import Base
from sbds.storages.db.utils import UniqueMixin


class Account(Base):
    """Steem Account Meta Class

    """

    __tablename__ = 'sbds_meta_accounts'
    name = Column(String(16), primary_key=True)


OPERATION_TO_ACCOUNT_FIELD_MAP = {'account_create': frozenset({'creator', 'new_account_name'}),
 'account_create_with_delegation': frozenset({'creator', 'new_account_name'}),
 'account_update': frozenset({'account'}),
 'account_witness_proxy': frozenset({'proxy', 'account'}),
 'account_witness_vote': frozenset({'witness', 'account'}),
 'author_reward': frozenset({'author'}),
 'block': frozenset({'witness'}),
 'cancel_transfer_from_savings': frozenset({'from'}),
 'challenge_authority': frozenset({'challenged', 'challenger'}),
 'change_recovery_account': frozenset({'account_to_recover',
                                       'new_recovery_account'}),
 'claim_reward_balance': frozenset({'account'}),
 'comment': frozenset({'parent_author', 'author'}),
 'comment_benefactor_reward': frozenset({'benefactor', 'author'}),
 'comment_options': frozenset({'author'}),
 'comment_payout_update': frozenset({'author'}),
 'comment_reward': frozenset({'author'}),
 'convert': frozenset({'owner'}),
 'curation_reward': frozenset({'comment_author', 'curator'}),
 'decline_voting_rights': frozenset({'account'}),
 'delegate_vesting_shares': frozenset({'delegatee', 'delegator'}),
 'delete_comment': frozenset({'author'}),
 'escrow_approve': frozenset({'from', 'who', 'to', 'agent'}),
 'escrow_dispute': frozenset({'from', 'who', 'to', 'agent'}),
 'escrow_release': frozenset({'from', 'receiver', 'who', 'to', 'agent'}),
 'escrow_transfer': frozenset({'from', 'to', 'agent'}),
 'feed_publish': frozenset({'publisher'}),
 'fill_convert_request': frozenset({'owner'}),
 'fill_order': frozenset({'open_owner', 'current_owner'}),
 'fill_transfer_from_savings': frozenset({'from', 'to'}),
 'fill_vesting_withdraw': frozenset({'to_account', 'from_account'}),
 'interest': frozenset({'owner'}),
 'limit_order_cancel': frozenset({'owner'}),
 'limit_order_create': frozenset({'owner'}),
 'limit_order_create2': frozenset({'owner'}),
 'liquidity_reward': frozenset({'owner'}),
 'pow': frozenset({'worker_account'}),
 'producer_reward': frozenset({'producer'}),
 'prove_authority': frozenset({'challenged'}),
 'recover_account': frozenset({'account_to_recover'}),
 'report_over_production': frozenset({'reporter'}),
 'request_account_recovery': frozenset({'account_to_recover',
                                        'recovery_account'}),
 'reset_account': frozenset({'account_to_reset', 'reset_account'}),
 'return_vesting_delegation': frozenset({'account'}),
 'set_reset_account': frozenset({'account',
                                 'current_reset_account',
                                 'reset_account'}),
 'set_withdraw_vesting_route': frozenset({'to_account', 'from_account'}),
 'shutdown_witness': frozenset({'owner'}),
 'transfer': frozenset({'from', 'to'}),
 'transfer_from_savings': frozenset({'from', 'to'}),
 'transfer_to_savings': frozenset({'from', 'to'}),
 'transfer_to_vesting': frozenset({'from', 'to'}),
 'vote': frozenset({'voter', 'author'}),
 'withdraw_vesting': frozenset({'account'}),
 'witness_update': frozenset({'owner'})}


ACCOUNT_NAME_EXTRACTORS = {
    'block': lambda op: (op.get('witness'),),
    'account_create': lambda op: (op.get('creator'),op.get('new_account_name'),),
    'account_create_with_delegation': lambda op: (op.get('creator'),op.get('new_account_name'),),
    'account_update': lambda op: (op.get('account'),),
    'comment': lambda op: (op.get('parent_author'),op.get('author'),),
    'comment_options': lambda op: (op.get('author'),),
    'challenge_authority': lambda op: (op.get('challenged'),op.get('challenger'),),
    'prove_authority': lambda op: (op.get('challenged'),),
    'delete_comment': lambda op: (op.get('author'),),
    'vote': lambda op: (op.get('voter'),op.get('author'),),
    'transfer': lambda op: (op.get('from'),op.get('to'),),
    'escrow_transfer': lambda op: (op.get('from'),op.get('to'),op.get('agent'),),
    'escrow_approve': lambda op: (op.get('from'),op.get('who'),op.get('to'),op.get('agent'),),
    'escrow_dispute': lambda op: (op.get('from'),op.get('who'),op.get('to'),op.get('agent'),),
    'escrow_release': lambda op: (op.get('from'),op.get('receiver'),op.get('who'),op.get('to'),op.get('agent'),),
    'transfer_to_vesting': lambda op: (op.get('from'),op.get('to'),),
    'withdraw_vesting': lambda op: (op.get('account'),),
    'set_withdraw_vesting_route': lambda op: (op.get('to_account'),op.get('from_account'),),
    'witness_update': lambda op: (op.get('owner'),),
    'account_witness_vote': lambda op: (op.get('witness'),op.get('account'),),
    'account_witness_proxy': lambda op: (op.get('proxy'),op.get('account'),),
    'feed_publish': lambda op: (op.get('publisher'),),
    'convert': lambda op: (op.get('owner'),),
    'limit_order_create': lambda op: (op.get('owner'),),
    'limit_order_create2': lambda op: (op.get('owner'),),
    'limit_order_cancel': lambda op: (op.get('owner'),),
    'pow': lambda op: (op.get('worker_account'),),
    'report_over_production': lambda op: (op.get('reporter'),),
    'request_account_recovery': lambda op: (op.get('account_to_recover'),op.get('recovery_account'),),
    'recover_account': lambda op: (op.get('account_to_recover'),),
    'reset_account': lambda op: (op.get('account_to_reset'),op.get('reset_account'),),
    'set_reset_account': lambda op: (op.get('current_reset_account'),op.get('reset_account'),op.get('account'),),
    'change_recovery_account': lambda op: (op.get('account_to_recover'),op.get('new_recovery_account'),),
    'transfer_to_savings': lambda op: (op.get('from'),op.get('to'),),
    'transfer_from_savings': lambda op: (op.get('from'),op.get('to'),),
    'cancel_transfer_from_savings': lambda op: (op.get('from'),),
    'decline_voting_rights': lambda op: (op.get('account'),),
    'claim_reward_balance': lambda op: (op.get('account'),),
    'delegate_vesting_shares': lambda op: (op.get('delegatee'),op.get('delegator'),),
    'author_reward': lambda op: (op.get('author'),),
    'curation_reward': lambda op: (op.get('comment_author'),op.get('curator'),),
    'comment_reward': lambda op: (op.get('author'),),
    'liquidity_reward': lambda op: (op.get('owner'),),
    'interest': lambda op: (op.get('owner'),),
    'fill_convert_request': lambda op: (op.get('owner'),),
    'fill_vesting_withdraw': lambda op: (op.get('to_account'),op.get('from_account'),),
    'shutdown_witness': lambda op: (op.get('owner'),),
    'fill_order': lambda op: (op.get('open_owner'),op.get('current_owner'),),
    'fill_transfer_from_savings': lambda op: (op.get('from'),op.get('to'),),
    'comment_payout_update': lambda op: (op.get('author'),),
    'return_vesting_delegation': lambda op: (op.get('account'),),
    'comment_benefactor_reward': lambda op: (op.get('benefactor'),op.get('author'),),
    'producer_reward': lambda op: (op.get('producer'),),
    }

def extract_account_names(prepared_ops):
    accounts_tuples = (ACCOUNT_NAME_EXTRACTORS[op['operation_type']](op) for op in prepared_ops if op['operation_type'] in ACCOUNT_NAME_EXTRACTORS)
    return set(acct for acct in it.chain(*accounts_tuples))
