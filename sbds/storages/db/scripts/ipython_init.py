# coding=utf-8
import os
import json

from sbds.storages.db.tables import Base
from sbds.storages.db.tables import Session

from sbds.storages.db.tables import Block

from sbds.storages.db.tables import TxBase
from sbds.storages.db.tables import TxAccountCreate
from sbds.storages.db.tables import TxAccountCreateWithDelegation
from sbds.storages.db.tables import TxAccountUpdate
from sbds.storages.db.tables import TxAccountWitnessProxy
from sbds.storages.db.tables import TxAccountWitnessVote
from sbds.storages.db.tables import TxCancelTransferFromSavings
from sbds.storages.db.tables import TxChangeRecoveryAccount
from sbds.storages.db.tables import TxClaimRewardBalance
from sbds.storages.db.tables import TxComment
from sbds.storages.db.tables import TxCommentOption
from sbds.storages.db.tables import TxConvert
from sbds.storages.db.tables import TxCustom
from sbds.storages.db.tables import TxCustomJSON
from sbds.storages.db.tables import TxDelegateVestingShares
from sbds.storages.db.tables import TxDeleteComment
from sbds.storages.db.tables import TxEscrowApprove
from sbds.storages.db.tables import TxEscrowDispute
from sbds.storages.db.tables import TxEscrowRelease
from sbds.storages.db.tables import TxEscrowTransfer
from sbds.storages.db.tables import TxFeedPublish
from sbds.storages.db.tables import TxLimitOrderCancel
from sbds.storages.db.tables import TxLimitOrderCreate
from sbds.storages.db.tables import TxPow
from sbds.storages.db.tables import TxPow2
from sbds.storages.db.tables import TxRecoverAccount
from sbds.storages.db.tables import TxRequestAccountRecovery
from sbds.storages.db.tables import TxWithdrawVestingRoute
from sbds.storages.db.tables import TxTransfer
from sbds.storages.db.tables import TxTransferFromSavings
from sbds.storages.db.tables import TxTransferToSavings
from sbds.storages.db.tables import TxTransferToVesting
from sbds.storages.db.tables import TxVote
from sbds.storages.db.tables import TxWithdrawVesting
from sbds.storages.db.tables import TxWitnessUpdate

from sbds.storages.db.utils import configure_engine
from sbds.http_client import SimpleSteemAPIClient


db_url = os.environ['DATABASE_URL']
rpc_url = os.environ['STEEMD_HTTP_URL']

engine_config = configure_engine(db_url)
engine = engine_config.engine
session = Session(bind=engine)
client = SimpleSteemAPIClient(url=rpc_url)
