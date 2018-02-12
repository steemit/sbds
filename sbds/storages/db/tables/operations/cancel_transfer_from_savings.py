# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class CancelTransferFromSavingsOperation(Base, BaseOperation):
    """Raw Format

    {
        "operations": [
            [
                "cancel_transfer_from_savings",
                {
                    "request_id": 1,
                    "from": "jesta"
                }
            ]
        ],
        "expiration": "2016-09-21T07:55:45",
        "signatures": [
            "1f135b1a9123672cdeb679d57272631858242f569c6066b0f69293963b6b7f7781587478587b843c7f9679855606c37f0ef16707bb03a775d78e2602540626e3d4"
        ],
        "ref_block_num": 45917,
        "ref_block_prefix": 2784823756,
        "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_cancel_transfer_from_savings'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    _from = Column('from', Unicode(50), index=True)
    request_id = Column(Integer)

    _fields = dict(
        _from=lambda x: x.get('from'),
        request_id=lambda x: x.get('request_id'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
