# coding=utf-8
import os
import json

from sbds.storages.db.tables import Base, Block
from sbds.storages.db.tables import Session

from sbds.storages.db.tables import BaseOperation
from sbds.storages.db.tables import AccountCreateOperation
from sbds.storages.db.tables import AccountCreateWithDelegationOperation
from sbds.storages.db.tables import AccountUpdateOperation
from sbds.storages.db.tables import AccountWitnessProxyOperation
from sbds.storages.db.tables import AccountWitnessVoteOperation
from sbds.storages.db.tables import CancelTransferFromSavingsOperation
from sbds.storages.db.tables import ChangeRecoveryAccountOperation
from sbds.storages.db.tables import ClaimRewardBalanceOperation
from sbds.storages.db.tables import CommentOperation
from sbds.storages.db.tables import CommentOptionOperation
from sbds.storages.db.tables import ConvertOperation
from sbds.storages.db.tables import CustomOperation
from sbds.storages.db.tables import CustomJSONOperation
from sbds.storages.db.tables import DelegateVestingSharesOperation
from sbds.storages.db.tables import DeleteCommentOperation
from sbds.storages.db.tables import EscrowApproveOperation
from sbds.storages.db.tables import EscrowDisputeOperation
from sbds.storages.db.tables import EscrowReleaseOperation
from sbds.storages.db.tables import EscrowTransferOperation
from sbds.storages.db.tables import FeedPublishOperation
from sbds.storages.db.tables import LimitOrderCancelOperation
from sbds.storages.db.tables import LimitOrderCreateOperation
from sbds.storages.db.tables import PowOperation
from sbds.storages.db.tables import Pow2Operation
from sbds.storages.db.tables import RecoverAccountOperation
from sbds.storages.db.tables import RequestAccountRecoveryOperation
from sbds.storages.db.tables import WithdrawVestingRouteOperation
from sbds.storages.db.tables import TransferOperation
from sbds.storages.db.tables import TransferFromSavingsOperation
from sbds.storages.db.tables import TransferToSavingsOperation
from sbds.storages.db.tables import TransferToVestingOperation
from sbds.storages.db.tables import VoteOperation
from sbds.storages.db.tables import WithdrawVestingOperation
from sbds.storages.db.tables import WitnessUpdateOperation

from sbds.storages.db.utils import configure_engine
from sbds.http_client import SimpleSteemAPIClient


db_url = os.environ['DATABASE_URL']
rpc_url = os.environ['STEEMD_HTTP_URL']

engine_config = configure_engine(db_url)
engine = engine_config.engine
session = Session(bind=engine)
client = SimpleSteemAPIClient(url=rpc_url)
