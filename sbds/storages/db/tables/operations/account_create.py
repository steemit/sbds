# coding=utf-8

import os.path


from sqlalchemy import Column, Numeric, Unicode, UnicodeText, Enum
from toolz import get_in

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation


class AccountCreateOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 3620775392,
        "expiration": "2016-03-30T07:05:03",
        "operations": [
            [
                "account_create",
                {
                    "owner": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM8MN3FNBa8WbEpxz3wGL3L1mkt6sGnncH8iuto7r8Wa3T9NSSGT",
                                1
                            ]
                        ]
                    },
                    "memo_key": "STM6Gkj27XMkoGsr4zwEvkjNhh4dykbXmPFzHhT8g86jWsqu3U38X",
                    "active": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM8HCf7QLUexogEviN8x1SpKRhFwg2sc8LrWuJqv7QsmWrua6ZyR",
                                1
                            ]
                        ]
                    },
                    "new_account_name": "fabian",
                    "posting": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM8EhGWcEuQ2pqCKkGHnbmcTNpWYZDjGTT7ketVBp4gUStDr2brz",
                                1
                            ]
                        ]
                    },
                    "creator": "hello",
                    "json_metadata": "{}",
                    "fee": "0.000 STEEM"
                }
            ]
        ],
        "signatures": [
            "2051b9c61cdd9df1f04e5d37529a72c9d4419c1e0b466d78c156c383aa951b21eb3f13b5bcbe9d0caf883143a15ff911c2d2cac9c466a7f619618bb3b4d24612b5"
        ],
        "ref_block_num": 29707,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "tx_id": 7973,
        "fee": 0.0000,
        "creator": "hello",
        "new_account_name": "fabian",
        "owner_key": "STM8MN3FNBa8WbEpxz3wGL3L1mkt6sGnncH8iuto7r8Wa3T9NSSGT",
        "active_key": "STM8HCf7QLUexogEviN8x1SpKRhFwg2sc8LrWuJqv7QsmWrua6ZyR",
        "posting_key": "STM8EhGWcEuQ2pqCKkGHnbmcTNpWYZDjGTT7ketVBp4gUStDr2brz",
        "memo_key": "STM6Gkj27XMkoGsr4zwEvkjNhh4dykbXmPFzHhT8g86jWsqu3U38X",
        "json_metadata": "{}"
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_account_creates'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    fee = Column(Numeric(15, 6), nullable=False)
    creator = Column(Unicode(50), nullable=False, index=True)
    new_account_name = Column(Unicode(50))
    owner_key = Column(Unicode(80), nullable=False)
    active_key = Column(Unicode(80), nullable=False)
    posting_key = Column(Unicode(80), nullable=False)
    memo_key = Column(Unicode(250), nullable=False)
    json_metadata = Column(UnicodeText)

    _fields = dict(
        creator=lambda x: x.get('creator'),
        fee=lambda x: amount_field(x.get('fee'), num_func=float),
        new_account_name=lambda x: x.get('new_account_name'),
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'),
        owner_key=lambda x: get_in(['owner', 'key_auths', 0, 0], x),
        active_key=lambda x: get_in(['active', 'key_auths', 0, 0], x),
        posting_key=lambda x: get_in(['posting', 'key_auths', 0, 0], x))

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)



