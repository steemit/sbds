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
    block_witness = relationship('Block',backref='account_witness',foreign_keys='Block.witness')
    account_create_creator = relationship('AccountCreateOperation',backref='account_creator',foreign_keys='AccountCreateOperation.creator')
    account_create_new_account_name = relationship('AccountCreateOperation',backref='account_new_account_name',foreign_keys='AccountCreateOperation.new_account_name')
    account_create_with_delegation_creator = relationship('AccountCreateWithDelegationOperation',backref='account_creator',foreign_keys='AccountCreateWithDelegationOperation.creator')
    account_create_with_delegation_new_account_name = relationship('AccountCreateWithDelegationOperation',backref='account_new_account_name',foreign_keys='AccountCreateWithDelegationOperation.new_account_name')
    account_update_account = relationship('AccountUpdateOperation',backref='account_account',foreign_keys='AccountUpdateOperation.account')
    comment_parent_author = relationship('CommentOperation',backref='account_parent_author',foreign_keys='CommentOperation.parent_author')
    comment_author = relationship('CommentOperation',backref='account_author',foreign_keys='CommentOperation.author')
    comment_options_author = relationship('CommentOptionsOperation',backref='account_author',foreign_keys='CommentOptionsOperation.author')
    challenge_authority_challenger = relationship('ChallengeAuthorityOperation',backref='account_challenger',foreign_keys='ChallengeAuthorityOperation.challenger')
    challenge_authority_challenged = relationship('ChallengeAuthorityOperation',backref='account_challenged',foreign_keys='ChallengeAuthorityOperation.challenged')
    prove_authority_challenged = relationship('ProveAuthorityOperation',backref='account_challenged',foreign_keys='ProveAuthorityOperation.challenged')
    delete_comment_author = relationship('DeleteCommentOperation',backref='account_author',foreign_keys='DeleteCommentOperation.author')
    vote_voter = relationship('VoteOperation',backref='account_voter',foreign_keys='VoteOperation.voter')
    vote_author = relationship('VoteOperation',backref='account_author',foreign_keys='VoteOperation.author')
    transfer_from = relationship('TransferOperation',backref='account_from',foreign_keys='TransferOperation._from')
    transfer_to = relationship('TransferOperation',backref='account_to',foreign_keys='TransferOperation.to')
    escrow_transfer_from = relationship('EscrowTransferOperation',backref='account_from',foreign_keys='EscrowTransferOperation._from')
    escrow_transfer_to = relationship('EscrowTransferOperation',backref='account_to',foreign_keys='EscrowTransferOperation.to')
    escrow_transfer_agent = relationship('EscrowTransferOperation',backref='account_agent',foreign_keys='EscrowTransferOperation.agent')
    escrow_approve_from = relationship('EscrowApproveOperation',backref='account_from',foreign_keys='EscrowApproveOperation._from')
    escrow_approve_to = relationship('EscrowApproveOperation',backref='account_to',foreign_keys='EscrowApproveOperation.to')
    escrow_approve_agent = relationship('EscrowApproveOperation',backref='account_agent',foreign_keys='EscrowApproveOperation.agent')
    escrow_approve_who = relationship('EscrowApproveOperation',backref='account_who',foreign_keys='EscrowApproveOperation.who')
    escrow_dispute_from = relationship('EscrowDisputeOperation',backref='account_from',foreign_keys='EscrowDisputeOperation._from')
    escrow_dispute_to = relationship('EscrowDisputeOperation',backref='account_to',foreign_keys='EscrowDisputeOperation.to')
    escrow_dispute_agent = relationship('EscrowDisputeOperation',backref='account_agent',foreign_keys='EscrowDisputeOperation.agent')
    escrow_dispute_who = relationship('EscrowDisputeOperation',backref='account_who',foreign_keys='EscrowDisputeOperation.who')
    escrow_release_from = relationship('EscrowReleaseOperation',backref='account_from',foreign_keys='EscrowReleaseOperation._from')
    escrow_release_to = relationship('EscrowReleaseOperation',backref='account_to',foreign_keys='EscrowReleaseOperation.to')
    escrow_release_agent = relationship('EscrowReleaseOperation',backref='account_agent',foreign_keys='EscrowReleaseOperation.agent')
    escrow_release_who = relationship('EscrowReleaseOperation',backref='account_who',foreign_keys='EscrowReleaseOperation.who')
    escrow_release_receiver = relationship('EscrowReleaseOperation',backref='account_receiver',foreign_keys='EscrowReleaseOperation.receiver')
    transfer_to_vesting_from = relationship('TransferToVestingOperation',backref='account_from',foreign_keys='TransferToVestingOperation._from')
    transfer_to_vesting_to = relationship('TransferToVestingOperation',backref='account_to',foreign_keys='TransferToVestingOperation.to')
    withdraw_vesting_account = relationship('WithdrawVestingOperation',backref='account_account',foreign_keys='WithdrawVestingOperation.account')
    set_withdraw_vesting_route_from_account = relationship('SetWithdrawVestingRouteOperation',backref='account_from_account',foreign_keys='SetWithdrawVestingRouteOperation.from_account')
    set_withdraw_vesting_route_to_account = relationship('SetWithdrawVestingRouteOperation',backref='account_to_account',foreign_keys='SetWithdrawVestingRouteOperation.to_account')
    witness_update_owner = relationship('WitnessUpdateOperation',backref='account_owner',foreign_keys='WitnessUpdateOperation.owner')
    account_witness_vote_account = relationship('AccountWitnessVoteOperation',backref='account_account',foreign_keys='AccountWitnessVoteOperation.account')
    account_witness_vote_witness = relationship('AccountWitnessVoteOperation',backref='account_witness',foreign_keys='AccountWitnessVoteOperation.witness')
    account_witness_proxy_account = relationship('AccountWitnessProxyOperation',backref='account_account',foreign_keys='AccountWitnessProxyOperation.account')
    account_witness_proxy_proxy = relationship('AccountWitnessProxyOperation',backref='account_proxy',foreign_keys='AccountWitnessProxyOperation.proxy')
    feed_publish_publisher = relationship('FeedPublishOperation',backref='account_publisher',foreign_keys='FeedPublishOperation.publisher')
    convert_owner = relationship('ConvertOperation',backref='account_owner',foreign_keys='ConvertOperation.owner')
    limit_order_create_owner = relationship('LimitOrderCreateOperation',backref='account_owner',foreign_keys='LimitOrderCreateOperation.owner')
    limit_order_create2_owner = relationship('LimitOrderCreate2Operation',backref='account_owner',foreign_keys='LimitOrderCreate2Operation.owner')
    limit_order_cancel_owner = relationship('LimitOrderCancelOperation',backref='account_owner',foreign_keys='LimitOrderCancelOperation.owner')
    pow_worker_account = relationship('PowOperation',backref='account_worker_account',foreign_keys='PowOperation.worker_account')
    report_over_production_reporter = relationship('ReportOverProductionOperation',backref='account_reporter',foreign_keys='ReportOverProductionOperation.reporter')
    request_account_recovery_recovery_account = relationship('RequestAccountRecoveryOperation',backref='account_recovery_account',foreign_keys='RequestAccountRecoveryOperation.recovery_account')
    request_account_recovery_account_to_recover = relationship('RequestAccountRecoveryOperation',backref='account_account_to_recover',foreign_keys='RequestAccountRecoveryOperation.account_to_recover')
    recover_account_account_to_recover = relationship('RecoverAccountOperation',backref='account_account_to_recover',foreign_keys='RecoverAccountOperation.account_to_recover')
    reset_account_reset_account = relationship('ResetAccountOperation',backref='account_reset_account',foreign_keys='ResetAccountOperation.reset_account')
    reset_account_account_to_reset = relationship('ResetAccountOperation',backref='account_account_to_reset',foreign_keys='ResetAccountOperation.account_to_reset')
    set_reset_account_account = relationship('SetResetAccountOperation',backref='account_account',foreign_keys='SetResetAccountOperation.account')
    set_reset_account_current_reset_account = relationship('SetResetAccountOperation',backref='account_current_reset_account',foreign_keys='SetResetAccountOperation.current_reset_account')
    set_reset_account_reset_account = relationship('SetResetAccountOperation',backref='account_reset_account',foreign_keys='SetResetAccountOperation.reset_account')
    change_recovery_account_account_to_recover = relationship('ChangeRecoveryAccountOperation',backref='account_account_to_recover',foreign_keys='ChangeRecoveryAccountOperation.account_to_recover')
    change_recovery_account_new_recovery_account = relationship('ChangeRecoveryAccountOperation',backref='account_new_recovery_account',foreign_keys='ChangeRecoveryAccountOperation.new_recovery_account')
    transfer_to_savings_from = relationship('TransferToSavingsOperation',backref='account_from',foreign_keys='TransferToSavingsOperation._from')
    transfer_to_savings_to = relationship('TransferToSavingsOperation',backref='account_to',foreign_keys='TransferToSavingsOperation.to')
    transfer_from_savings_from = relationship('TransferFromSavingsOperation',backref='account_from',foreign_keys='TransferFromSavingsOperation._from')
    transfer_from_savings_to = relationship('TransferFromSavingsOperation',backref='account_to',foreign_keys='TransferFromSavingsOperation.to')
    cancel_transfer_from_savings_from = relationship('CancelTransferFromSavingsOperation',backref='account_from',foreign_keys='CancelTransferFromSavingsOperation._from')
    decline_voting_rights_account = relationship('DeclineVotingRightsOperation',backref='account_account',foreign_keys='DeclineVotingRightsOperation.account')
    claim_reward_balance_account = relationship('ClaimRewardBalanceOperation',backref='account_account',foreign_keys='ClaimRewardBalanceOperation.account')
    delegate_vesting_shares_delegator = relationship('DelegateVestingSharesOperation',backref='account_delegator',foreign_keys='DelegateVestingSharesOperation.delegator')
    delegate_vesting_shares_delegatee = relationship('DelegateVestingSharesOperation',backref='account_delegatee',foreign_keys='DelegateVestingSharesOperation.delegatee')
    author_reward_author = relationship('AuthorRewardVirtualOperation',backref='account_author',foreign_keys='AuthorRewardVirtualOperation.author')
    curation_reward_curator = relationship('CurationRewardVirtualOperation',backref='account_curator',foreign_keys='CurationRewardVirtualOperation.curator')
    curation_reward_comment_author = relationship('CurationRewardVirtualOperation',backref='account_comment_author',foreign_keys='CurationRewardVirtualOperation.comment_author')
    comment_reward_author = relationship('CommentRewardVirtualOperation',backref='account_author',foreign_keys='CommentRewardVirtualOperation.author')
    liquidity_reward_owner = relationship('LiquidityRewardVirtualOperation',backref='account_owner',foreign_keys='LiquidityRewardVirtualOperation.owner')
    interest_owner = relationship('InterestVirtualOperation',backref='account_owner',foreign_keys='InterestVirtualOperation.owner')
    fill_convert_request_owner = relationship('FillConvertRequestVirtualOperation',backref='account_owner',foreign_keys='FillConvertRequestVirtualOperation.owner')
    fill_vesting_withdraw_from_account = relationship('FillVestingWithdrawVirtualOperation',backref='account_from_account',foreign_keys='FillVestingWithdrawVirtualOperation.from_account')
    fill_vesting_withdraw_to_account = relationship('FillVestingWithdrawVirtualOperation',backref='account_to_account',foreign_keys='FillVestingWithdrawVirtualOperation.to_account')
    shutdown_witness_owner = relationship('ShutdownWitnessVirtualOperation',backref='account_owner',foreign_keys='ShutdownWitnessVirtualOperation.owner')
    fill_order_current_owner = relationship('FillOrderVirtualOperation',backref='account_current_owner',foreign_keys='FillOrderVirtualOperation.current_owner')
    fill_order_open_owner = relationship('FillOrderVirtualOperation',backref='account_open_owner',foreign_keys='FillOrderVirtualOperation.open_owner')
    fill_transfer_from_savings_from = relationship('FillTransferFromSavingsVirtualOperation',backref='account_from',foreign_keys='FillTransferFromSavingsVirtualOperation._from')
    fill_transfer_from_savings_to = relationship('FillTransferFromSavingsVirtualOperation',backref='account_to',foreign_keys='FillTransferFromSavingsVirtualOperation.to')
    comment_payout_update_author = relationship('CommentPayoutUpdateVirtualOperation',backref='account_author',foreign_keys='CommentPayoutUpdateVirtualOperation.author')
    return_vesting_delegation_account = relationship('ReturnVestingDelegationVirtualOperation',backref='account_account',foreign_keys='ReturnVestingDelegationVirtualOperation.account')
    comment_benefactor_reward_benefactor = relationship('CommentBenefactorRewardVirtualOperation',backref='account_benefactor',foreign_keys='CommentBenefactorRewardVirtualOperation.benefactor')
    comment_benefactor_reward_author = relationship('CommentBenefactorRewardVirtualOperation',backref='account_author',foreign_keys='CommentBenefactorRewardVirtualOperation.author')
    producer_reward_producer = relationship('ProducerRewardVirtualOperation',backref='account_producer',foreign_keys='ProducerRewardVirtualOperation.producer')
    


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
    return set(acct for acct in it.chain(*accounts_tuples) if acct)
