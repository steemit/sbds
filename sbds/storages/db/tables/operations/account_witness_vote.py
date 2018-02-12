# coding=utf-8

import os.path

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class AccountWitnessVoteOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 575883867,
        "operations": [
            [
                "account_witness_vote",
                {
                    "witness": "berniesanders",
                    "account": "donalddrumpf",
                    "approve": true
                }
            ]
        ],
        "signatures": [
            "1f7782f6c379d14c97718489b5ebca68fa25b3042e781d2f620ccc4927fbf4d3f30e60ba424cd906eb75b87cd4002bf982bc2ba9dc0f2c7b136b566de7416a170b"
        ],
        "ref_block_num": 57831,
        "expiration": "2016-03-28T23:43:36",
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "tx_id": 6055,
        "witness": "berniesanders",
        "id": 1,
        "account": "donalddrumpf",
        "approve": True
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_account_witness_votes'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    account = Column(Unicode(50), nullable=False)
    witness = Column(Unicode(50), nullable=False)
    approve = Column(Boolean, default=False)

    _fields = dict(
        account=lambda x: x.get('account'),
        approve=lambda x: x.get('approve'),
        witness=lambda x: x.get('witness'))
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
