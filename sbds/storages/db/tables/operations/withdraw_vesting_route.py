# coding=utf-8

import os.path

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import SmallInteger
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class WithdrawVestingRouteOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 1734342499,
        "expiration": "2016-07-01T14:12:24",
        "operations": [
            [
                "set_withdraw_vesting_route",
                {
                    "from_account": "lin9uxis",
                    "percent": 10000,
                    "auto_vest": false,
                    "to_account": "linouxis9"
                }
            ]
        ],
        "signatures": [
            "1f1fb84928c952d6bec647f8180787485165714762591096655b9f44ad8b35742a0b964faa5d40b4ff66602ff5e5d978153414abf166adf90b6926e4791164c76a"
        ],
        "ref_block_num": 1756,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 9,
        "tx_id": 454420,
        "from_account": "lin9uxis",
        "to_account": "linouxis9",
        "percent": 10000,
        "auto_vest": False
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_withdraw_vesting_routes'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    from_account = Column(Unicode(50), nullable=False)
    to_account = Column(Unicode(50), nullable=False)
    percent = Column(SmallInteger, nullable=False)
    auto_vest = Column(Boolean)

    _fields = dict(
        from_account=lambda x: x.get('from_account'),
        to_account=lambda x: x.get('to_account'),
        percent=lambda x: x.get('percent'),
        auto_vest=lambda x: x.get('auto_vest'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
