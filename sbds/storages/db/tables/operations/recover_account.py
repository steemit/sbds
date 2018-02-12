# coding=utf-8

import os.path

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class RecoverAccountOperation(Base, BaseOperation):
    """
    {
        "operations": [
            [
                "recover_account",
                {
                    "recent_owner_authority": {
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM6Wf68LVi22QC9eS8LBWykRiSrKKp5RTWXcNqjh3VPNhiT9xFxx",
                                1
                            ]
                        ],
                        "weight_threshold": 1
                    },
                    "new_owner_authority": {
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM82miH8qam2G2WPPjgyquPBrUbenGDHjhZMxqaKqCugWhcuqZzW",
                                1
                            ]
                        ],
                        "weight_threshold": 1
                    },
                    "extensions": [],
                    "account_to_recover": "steemychicken1"
                }
            ]
        ],
        "expiration": "2016-07-18T05:46:33",
        "signatures": [
            "202c2c3902d513bb7f22e833576ea8418fdf7be3a08b0736d1de03c3289c5db11e1a95af820703e1407b8f3c0b030d857f666132b10be165b7569faba0442790f5",
            "2059587d734535c43caf33a706404d813897e8887ad1696750435be63dfae26fde5995a2c6c8cf295c380d89152abe97f4990f9c78a0e9095a96e6e2432dd88e05"
        ],
        "ref_block_num": 17711,
        "ref_block_prefix": 311057647,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_recover_accounts'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    recovery_account = Column(Unicode(50))
    account_to_recover = Column(Unicode(50), nullable=False)
    recovered = Column(Boolean, default=False)

    _fields = dict(
        recovery_account=lambda x: x.get('recovery_account'),
        account_to_recover=lambda x: x.get('account_to_recover'),
        recovered=lambda x: True)

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
