# -*- coding: utf-8 -*-
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

metadata = MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker()

# pylint: disable=wrong-import-position
from ..utils import isolated_nullpool_engine
from .core import Block

from .tx import TxBase
from .tx import TxAccountCreate
from .tx import TxAccountCreateWithDelegation
from .tx import TxAccountUpdate
from .tx import TxAccountWitnessProxy
from .tx import TxAccountWitnessVote
from .tx import TxCancelTransferFromSavings
from .tx import TxChangeRecoveryAccount
from .tx import TxClaimRewardBalance
from .tx import TxComment
from .tx import TxCommentOption
from .tx import TxConvert
from .tx import TxCustom
from .tx import TxCustomJSON
from .tx import TxDelegateVestingShares
from .tx import TxDeleteComment
from .tx import TxEscrowApprove
from .tx import TxEscrowDispute
from .tx import TxEscrowRelease
from .tx import TxEscrowTransfer
from .tx import TxFeedPublish
from .tx import TxLimitOrderCancel
from .tx import TxLimitOrderCreate
from .tx import TxPow
from .tx import TxPow2
from .tx import TxRecoverAccount
from .tx import TxRequestAccountRecovery
from .tx import TxWithdrawVestingRoute
from .tx import TxTransfer
from .tx import TxTransferFromSavings
from .tx import TxTransferToSavings
from .tx import TxTransferToVesting
from .tx import TxVote
from .tx import TxWithdrawVesting
from .tx import TxWitnessUpdate


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
