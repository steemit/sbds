# -*- coding: utf-8 -*-
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

metadata = MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker()

# pylint: disable=wrong-import-position
from ..utils import isolated_nullpool_engine
from sbds.storages.db.tables.block import Block

from .operations import BaseOperation
from .operations import AccountCreateOperation
from .operations import AccountCreateWithDelegationOperation
from .operations import AccountUpdateOperation
from .operations import AccountWitnessProxyOperation
from .operations import AccountWitnessVoteOperation
from .operations import CancelTransferFromSavingsOperation
from .operations import ChangeRecoveryAccountOperation
from .operations import ClaimRewardBalanceOperation
from .operations import CommentOperation
from .operations import CommentOptionOperation
from .operations import ConvertOperation
from .operations import CustomOperation
from .operations import CustomJSONOperation
from .operations import DelegateVestingSharesOperation
from .operations import DeleteCommentOperation
from .operations import EscrowApproveOperation
from .operations import EscrowDisputeOperation
from .operations import EscrowReleaseOperation
from .operations import EscrowTransferOperation
from .operations import FeedPublishOperation
from .operations import LimitOrderCancelOperation
from .operations import LimitOrderCreateOperation
from .operations import PowOperation
from .operations import Pow2Operation
from .operations import RecoverAccountOperation
from .operations import RequestAccountRecoveryOperation
from .operations import WithdrawVestingRouteOperation
from .operations import TransferOperation
from .operations import TransferFromSavingsOperation
from .operations import TransferToSavingsOperation
from .operations import TransferToVestingOperation
from .operations import VoteOperation
from .operations import WithdrawVestingOperation
from .operations import WitnessUpdateOperation


def init_tables(database_url, _metadata, checkfirst=True):
    """Create any missing tables on the database"""
    with isolated_nullpool_engine(database_url) as engine:
        _metadata.create_all(bind=engine, checkfirst=checkfirst)


def reset_tables(database_url, _metadata):
    """Drop and then create tables on the database"""

    # use reflected MetaData to avoid errors due to ORM classes
    # being inconsistent with existing tables
    with isolated_nullpool_engine(database_url) as engine:
        seperate_metadata = MetaData()
        seperate_metadata.reflect(bind=engine)
        seperate_metadata.drop_all(bind=engine)

    # use ORM clases to define tables to create
    init_tables(database_url, _metadata)


def test_connection(database_url):
    _metadata = MetaData()
    with isolated_nullpool_engine(database_url) as engine:
        try:
            _metadata.reflect(bind=engine)
            table_count = len(_metadata.tables)
            url = engine.url
            return url, table_count
        except Exception as e:
            return False, e


def get_table_count(database_url):
    return len(get_tables(database_url))


def get_tables(database_url):
    with isolated_nullpool_engine(database_url) as engine:
        tables = engine.table_names()
    return tables
