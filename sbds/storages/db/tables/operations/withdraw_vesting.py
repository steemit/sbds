# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from .base import BaseOperation


class WithdrawVestingOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 4265937178,
        "expiration": "2016-03-31T18:52:33",
        "operations": [
            [
                "withdraw_vesting",
                {
                    "account": "steemit",
                    "vesting_shares": "260000.000000 VESTS"
                }
            ]
        ],
        "signatures": [
            "2056b5be4b9d12f91e3cec198e74dd048bcfded95b92291709815c0afc069e5aa44c1a62e3aca0001a50d57010a870975c576f83de42e435f8634dcde52a8764c5"
        ],
        "ref_block_num": 7003,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 2,
        "tx_id": 10275,
        "account": "steemit",
        "vesting_shares": 260000.0000
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_withdraw_vestings'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    account = Column(Unicode(50), nullable=False)
    vesting_shares = Column(Numeric(25, 6), nullable=False, default=0.0)

    _fields = dict(
        account=lambda x: x.get('account'),
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
