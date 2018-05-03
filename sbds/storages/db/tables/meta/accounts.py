# -*- coding: utf-8 -*-
import itertools as it

from funcy import flatten
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Text

from sbds.storages.db.tables import Base


class Account(Base):
    """Steem Account Meta Class

    """

    __tablename__ = 'sbds_meta_accounts'
    _id = Column(BigInteger, autoincrement=True, primary_key=True)
    name = Column(Text, unique=True)


OPERATION_TO_ACCOUNT_FIELD_MAP = {
    'account_create':
    frozenset({'creator', 'new_account_name'}),
    'account_create_with_delegation':
    frozenset({'creator', 'new_account_name'}),
    'account_update':
    frozenset({'account'}),
    'account_witness_proxy':
    frozenset({'account', 'proxy'}),
    'account_witness_vote':
    frozenset({'account', 'witness'}),
    'author_reward':
    frozenset({'author'}),
    'block':
    frozenset({'witness'}),
    'cancel_transfer_from_savings':
    frozenset({'from'}),
    'challenge_authority':
    frozenset({'challenger', 'challenged'}),
    'change_recovery_account':
    frozenset({'account_to_recover', 'new_recovery_account'}),
    'claim_reward_balance':
    frozenset({'account'}),
    'comment':
    frozenset({'author', 'parent_author'}),
    'comment_benefactor_reward':
    frozenset({'author', 'benefactor'}),
    'comment_options':
    frozenset({'author'}),
    'comment_payout_update':
    frozenset({'author'}),
    'comment_reward':
    frozenset({'author'}),
    'convert':
    frozenset({'owner'}),
    'curation_reward':
    frozenset({'curator', 'comment_author'}),
    'custom':
    frozenset({'required_auths'}),
    'custom_binary':
    frozenset({
        'required_active_auths', 'required_owner_auths',
        'required_posting_auths'
    }),
    'custom_json':
    frozenset({'required_posting_auths', 'required_auths'}),
    'decline_voting_rights':
    frozenset({'account'}),
    'delegate_vesting_shares':
    frozenset({'delegator', 'delegatee'}),
    'delete_comment':
    frozenset({'author'}),
    'escrow_approve':
    frozenset({'to', 'who', 'from', 'agent'}),
    'escrow_dispute':
    frozenset({'to', 'who', 'from', 'agent'}),
    'escrow_release':
    frozenset({'receiver', 'who', 'from', 'to', 'agent'}),
    'escrow_transfer':
    frozenset({'to', 'from', 'agent'}),
    'feed_publish':
    frozenset({'publisher'}),
    'fill_convert_request':
    frozenset({'owner'}),
    'fill_order':
    frozenset({'open_owner', 'current_owner'}),
    'fill_transfer_from_savings':
    frozenset({'to', 'from'}),
    'fill_vesting_withdraw':
    frozenset({'to_account', 'from_account'}),
    'interest':
    frozenset({'owner'}),
    'limit_order_cancel':
    frozenset({'owner'}),
    'limit_order_create':
    frozenset({'owner'}),
    'limit_order_create2':
    frozenset({'owner'}),
    'liquidity_reward':
    frozenset({'owner'}),
    'pow':
    frozenset({'worker_account'}),
    'producer_reward':
    frozenset({'producer'}),
    'prove_authority':
    frozenset({'challenged'}),
    'recover_account':
    frozenset({'account_to_recover'}),
    'report_over_production':
    frozenset({'reporter'}),
    'request_account_recovery':
    frozenset({'account_to_recover', 'recovery_account'}),
    'reset_account':
    frozenset({'reset_account', 'account_to_reset'}),
    'return_vesting_delegation':
    frozenset({'account'}),
    'set_reset_account':
    frozenset({'account', 'current_reset_account', 'reset_account'}),
    'set_withdraw_vesting_route':
    frozenset({'to_account', 'from_account'}),
    'shutdown_witness':
    frozenset({'owner'}),
    'transfer':
    frozenset({'to', 'from'}),
    'transfer_from_savings':
    frozenset({'to', 'from'}),
    'transfer_to_savings':
    frozenset({'to', 'from'}),
    'transfer_to_vesting':
    frozenset({'to', 'from'}),
    'vote':
    frozenset({'author', 'voter'}),
    'withdraw_vesting':
    frozenset({'account'}),
    'witness_update':
    frozenset({'owner'})
}


ACCOUNT_NAME_EXTRACTORS = {
    'block': lambda op: [acct for acct in set(flatten((op.get('witness'),))) if acct],
    'account_create': lambda op: [acct for acct in set(flatten((op.get('creator'), op.get('new_account_name'),))) if acct],
    'account_create_with_delegation': lambda op: [acct for acct in set(flatten((op.get('creator'), op.get('new_account_name'),))) if acct],
    'account_update': lambda op: [acct for acct in set(flatten((op.get('account'),))) if acct],
    'comment': lambda op: [acct for acct in set(flatten((op.get('author'), op.get('parent_author'),))) if acct],
    'comment_options': lambda op: [acct for acct in set(flatten((op.get('author'),))) if acct],
    'challenge_authority': lambda op: [acct for acct in set(flatten((op.get('challenger'), op.get('challenged'),))) if acct],
    'prove_authority': lambda op: [acct for acct in set(flatten((op.get('challenged'),))) if acct],
    'delete_comment': lambda op: [acct for acct in set(flatten((op.get('author'),))) if acct],
    'vote': lambda op: [acct for acct in set(flatten((op.get('author'), op.get('voter'),))) if acct],
    'transfer': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('from'),))) if acct],
    'escrow_transfer': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('from'), op.get('agent'),))) if acct],
    'escrow_approve': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('who'), op.get('from'), op.get('agent'),))) if acct],
    'escrow_dispute': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('who'), op.get('from'), op.get('agent'),))) if acct],
    'escrow_release': lambda op: [acct for acct in set(flatten((op.get('receiver'), op.get('who'), op.get('from'), op.get('to'), op.get('agent'),))) if acct],
    'transfer_to_vesting': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('from'),))) if acct],
    'withdraw_vesting': lambda op: [acct for acct in set(flatten((op.get('account'),))) if acct],
    'set_withdraw_vesting_route': lambda op: [acct for acct in set(flatten((op.get('to_account'), op.get('from_account'),))) if acct],
    'witness_update': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'account_witness_vote': lambda op: [acct for acct in set(flatten((op.get('account'), op.get('witness'),))) if acct],
    'account_witness_proxy': lambda op: [acct for acct in set(flatten((op.get('account'), op.get('proxy'),))) if acct],
    'custom': lambda op: [acct for acct in set(flatten((op.get('required_auths'),))) if acct],
    'custom_json': lambda op: [acct for acct in set(flatten((op.get('required_posting_auths'), op.get('required_auths'),))) if acct],
    'custom_binary': lambda op: [acct for acct in set(flatten((op.get('required_active_auths'), op.get('required_posting_auths'), op.get('required_owner_auths'),))) if acct],
    'feed_publish': lambda op: [acct for acct in set(flatten((op.get('publisher'),))) if acct],
    'convert': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'limit_order_create': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'limit_order_create2': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'limit_order_cancel': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'pow': lambda op: [acct for acct in set(flatten((op.get('worker_account'),))) if acct],
    'report_over_production': lambda op: [acct for acct in set(flatten((op.get('reporter'),))) if acct],
    'request_account_recovery': lambda op: [acct for acct in set(flatten((op.get('recovery_account'), op.get('account_to_recover'),))) if acct],
    'recover_account': lambda op: [acct for acct in set(flatten((op.get('account_to_recover'),))) if acct],
    'reset_account': lambda op: [acct for acct in set(flatten((op.get('reset_account'), op.get('account_to_reset'),))) if acct],
    'set_reset_account': lambda op: [acct for acct in set(flatten((op.get('current_reset_account'), op.get('reset_account'), op.get('account'),))) if acct],
    'change_recovery_account': lambda op: [acct for acct in set(flatten((op.get('new_recovery_account'), op.get('account_to_recover'),))) if acct],
    'transfer_to_savings': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('from'),))) if acct],
    'transfer_from_savings': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('from'),))) if acct],
    'cancel_transfer_from_savings': lambda op: [acct for acct in set(flatten((op.get('from'),))) if acct],
    'decline_voting_rights': lambda op: [acct for acct in set(flatten((op.get('account'),))) if acct],
    'claim_reward_balance': lambda op: [acct for acct in set(flatten((op.get('account'),))) if acct],
    'delegate_vesting_shares': lambda op: [acct for acct in set(flatten((op.get('delegator'), op.get('delegatee'),))) if acct],
    'author_reward': lambda op: [acct for acct in set(flatten((op.get('author'),))) if acct],
    'curation_reward': lambda op: [acct for acct in set(flatten((op.get('curator'), op.get('comment_author'),))) if acct],
    'comment_reward': lambda op: [acct for acct in set(flatten((op.get('author'),))) if acct],
    'liquidity_reward': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'interest': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'fill_convert_request': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'fill_vesting_withdraw': lambda op: [acct for acct in set(flatten((op.get('to_account'), op.get('from_account'),))) if acct],
    'shutdown_witness': lambda op: [acct for acct in set(flatten((op.get('owner'),))) if acct],
    'fill_order': lambda op: [acct for acct in set(flatten((op.get('open_owner'), op.get('current_owner'),))) if acct],
    'fill_transfer_from_savings': lambda op: [acct for acct in set(flatten((op.get('to'), op.get('from'),))) if acct],
    'comment_payout_update': lambda op: [acct for acct in set(flatten((op.get('author'),))) if acct],
    'return_vesting_delegation': lambda op: [acct for acct in set(flatten((op.get('account'),))) if acct],
    'comment_benefactor_reward': lambda op: [acct for acct in set(flatten((op.get('author'), op.get('benefactor'),))) if acct],
    'producer_reward': lambda op: [acct for acct in set(flatten((op.get('producer'),))) if acct],
}


def extract_account_names(prepared_ops):
    accounts_tuples = (ACCOUNT_NAME_EXTRACTORS[op['operation_type']](op)
                       for op in prepared_ops
                       if op['operation_type'] in ACCOUNT_NAME_EXTRACTORS)
    return set(acct for acct in it.chain(*accounts_tuples) if acct)
