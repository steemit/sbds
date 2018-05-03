# -*- coding: utf-8 -*-
# Operations
from .account_create import AccountCreateOperation
from .account_create_with_delegation import \
    AccountCreateWithDelegationOperation
from .account_update import AccountUpdateOperation
from .account_witness_proxy import AccountWitnessProxyOperation
from .account_witness_vote import AccountWitnessVoteOperation
from .cancel_transfer_from_savings import CancelTransferFromSavingsOperation
from .challenge_authority import ChallengeAuthorityOperation
from .change_recovery_account import ChangeRecoveryAccountOperation
from .claim_reward_balance import ClaimRewardBalanceOperation
from .comment import CommentOperation
from .comment_options import CommentOptionsOperation
from .convert import ConvertOperation
from .custom import CustomOperation
from .custom_binary import CustomBinaryOperation
from .custom_json import CustomJsonOperation
from .decline_voting_rights import DeclineVotingRightsOperation
from .delegate_vesting_shares import DelegateVestingSharesOperation
from .delete_comment import DeleteCommentOperation
from .escrow_approve import EscrowApproveOperation
from .escrow_dispute import EscrowDisputeOperation
from .escrow_release import EscrowReleaseOperation
from .escrow_transfer import EscrowTransferOperation
from .feed_publish import FeedPublishOperation
from .limit_order_cancel import LimitOrderCancelOperation
from .limit_order_create import LimitOrderCreateOperation
from .limit_order_create2 import LimitOrderCreate2Operation
from .pow import PowOperation
from .pow2 import Pow2Operation
from .prove_authority import ProveAuthorityOperation
from .recover_account import RecoverAccountOperation
from .report_over_production import ReportOverProductionOperation
from .request_account_recovery import RequestAccountRecoveryOperation
from .reset_account import ResetAccountOperation
from .set_reset_account import SetResetAccountOperation
from .set_withdraw_vesting_route import SetWithdrawVestingRouteOperation
from .transfer import TransferOperation
from .transfer_from_savings import TransferFromSavingsOperation
from .transfer_to_savings import TransferToSavingsOperation
from .transfer_to_vesting import TransferToVestingOperation
from .vote import VoteOperation
from .withdraw_vesting import WithdrawVestingOperation
from .witness_update import WitnessUpdateOperation

# Virtual Operations
from .virtual.author_reward import AuthorRewardVirtualOperation
from .virtual.curation_reward import CurationRewardVirtualOperation
from .virtual.comment_reward import CommentRewardVirtualOperation
from .virtual.liquidity_reward import LiquidityRewardVirtualOperation
from .virtual.interest import InterestVirtualOperation
from .virtual.fill_convert_request import FillConvertRequestVirtualOperation
from .virtual.fill_vesting_withdraw import FillVestingWithdrawVirtualOperation
from .virtual.shutdown_witness import ShutdownWitnessVirtualOperation
from .virtual.fill_order import FillOrderVirtualOperation
from .virtual.fill_transfer_from_savings import FillTransferFromSavingsVirtualOperation
from .virtual.hardfork import HardforkVirtualOperation
from .virtual.comment_payout_update import CommentPayoutUpdateVirtualOperation
from .virtual.return_vesting_delegation import ReturnVestingDelegationVirtualOperation
from .virtual.comment_benefactor_reward import CommentBenefactorRewardVirtualOperation
from .virtual.producer_reward import ProducerRewardVirtualOperation

# pylint: disable=line-too-long, bad-continuation, too-many-lines, no-self-argument

# These are defined in the steem source code here:
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/operations.hpp
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/steem_operations.hpp
op_class_map = {
    'account_create': AccountCreateOperation,
    'account_create_with_delegation': AccountCreateWithDelegationOperation,
    'account_update': AccountUpdateOperation,
    'account_witness_proxy': AccountWitnessProxyOperation,
    'account_witness_vote': AccountWitnessVoteOperation,
    'cancel_transfer_from_savings': CancelTransferFromSavingsOperation,
    'challenge_authority': ChallengeAuthorityOperation,
    'change_recovery_account': ChangeRecoveryAccountOperation,
    'claim_reward_balance': ClaimRewardBalanceOperation,
    'comment': CommentOperation,
    'comment_options': CommentOptionsOperation,
    'convert': ConvertOperation,
    'custom': CustomOperation,
    'custom_binary': CustomBinaryOperation,
    'custom_json': CustomJsonOperation,
    'decline_voting_rights': DeclineVotingRightsOperation,
    'delegate_vesting_shares': DelegateVestingSharesOperation,
    'delete_comment': DeleteCommentOperation,
    'escrow_approve': EscrowApproveOperation,
    'escrow_dispute': EscrowDisputeOperation,
    'escrow_release': EscrowReleaseOperation,
    'escrow_transfer': EscrowTransferOperation,
    'feed_publish': FeedPublishOperation,
    'limit_order_cancel': LimitOrderCancelOperation,
    'limit_order_create': LimitOrderCreateOperation,
    'limit_order_create2': LimitOrderCreate2Operation,
    'pow': PowOperation,
    'pow2': Pow2Operation,
    'prove_authority': ProveAuthorityOperation,
    'recover_account': RecoverAccountOperation,
    'report_over_production': ReportOverProductionOperation,
    'request_account_recovery': RequestAccountRecoveryOperation,
    'reset_account': ResetAccountOperation,
    'set_reset_account': SetResetAccountOperation,
    'set_withdraw_vesting_route': SetWithdrawVestingRouteOperation,
    'transfer': TransferOperation,
    'transfer_from_savings': TransferFromSavingsOperation,
    'transfer_to_savings': TransferToSavingsOperation,
    'transfer_to_vesting': TransferToVestingOperation,
    'vote': VoteOperation,
    'withdraw_vesting': WithdrawVestingOperation,
    'witness_update': WitnessUpdateOperation
}


# virtual operations
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/steem_virtual_operations.hpp
virtual_op_class_map = {
    'author_reward': AuthorRewardVirtualOperation,
    'curation_reward': CurationRewardVirtualOperation,
    'comment_reward': CommentRewardVirtualOperation,
    'liquidity_reward': LiquidityRewardVirtualOperation,
    'interest': InterestVirtualOperation,
    'fill_convert_request': FillConvertRequestVirtualOperation,
    'fill_vesting_withdraw': FillVestingWithdrawVirtualOperation,
    'shutdown_witness': ShutdownWitnessVirtualOperation,
    'fill_order': FillOrderVirtualOperation,
    'fill_transfer_from_savings': FillTransferFromSavingsVirtualOperation,
    'hardfork': HardforkVirtualOperation,
    'comment_payout_update': CommentPayoutUpdateVirtualOperation,
    'return_vesting_delegation': ReturnVestingDelegationVirtualOperation,
    'comment_benefactor_reward': CommentBenefactorRewardVirtualOperation,
    'producer_reward': ProducerRewardVirtualOperation
}

combined_ops_class_map = dict(**op_class_map, **virtual_op_class_map)

combined_ops_db_table_map = {
    k: combined_ops_class_map[k].__tablename__.replace(
        '_operation',
        '') for k in combined_ops_class_map.keys()}


class UndefinedTransactionType(Exception):
    """Exception raised when undefined transction is encountered"""


def op_class_for_type(op_type):
    return combined_ops_class_map[op_type]


def op_db_table_for_type(op_type):
    return combined_ops_db_table_map[op_type]
