# coding=utf-8

import os.path

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class RequestAccountRecoveryOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 392888852,
        "expiration": "2016-07-18T00:14:45",
        "operations": [
            [
                "request_account_recovery",
                {
                    "account_to_recover": "gandalf",
                    "new_owner_authority": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM6LYxj96zdypHYqgDdD6Nyh2NxerN3P1Mp3ddNm7gci63nfrSuZ",
                                1
                            ]
                        ]
                    },
                    "recovery_account": "steem",
                    "extensions": []
                }
            ]
        ],
        "signatures": [
            "1f6b0f44985aa8f476385078b69366b0868b45b666f717b34e074b98ca97a767b6209a931e998912f51b2f7d490a6283c3ce9c3d1f2a42a4695bda1e7a6786d0d3"
        ],
        "ref_block_num": 11112,
    "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_request_account_recoveries'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    recovery_account = Column(Unicode(50))
    account_to_recover = Column(Unicode(50), nullable=False)
    recovered = Column(Boolean, default=False)

    _fields = dict(
        # FIXME
        operation_num=lambda x: x.get('operation_num'),
        recovery_account=lambda x: x.get('recovery_account'),
        account_to_recover=lambda x: x.get('account_to_recover'),
        recovered=lambda x: False)

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
