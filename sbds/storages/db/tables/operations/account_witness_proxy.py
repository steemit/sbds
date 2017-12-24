# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Enum

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class AccountWitnessProxyOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 2749880717,
        "operations": [
            [
                "account_witness_proxy",
                {
                    "proxy": "abit",
                    "account": "puppies"
                }
            ]
        ],
        "signatures": [
            "2066825bf5033b1a85b3f26c43bc853aa2e1e57ecdd400f61ea0ed444906836c323345c6b04cdbbb39637ed180ddf7a8eacc9d36086158140d1dec5788b73a01b4"
        ],
        "ref_block_num": 31712,
        "expiration": "2016-04-08T15:47:00",
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 22,
        "tx_id": 44236,
        "account": "puppies",
        "Proxy": "abit"
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_account_witness_proxies'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    account = Column(Unicode(50), nullable=False)
    Proxy = Column(Unicode(50), nullable=False)

    _fields = dict(
        account=lambda x: x.get('account'),
        Proxy=lambda x: x.get('proxy'),  # TODO fix capitalization
    )

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

