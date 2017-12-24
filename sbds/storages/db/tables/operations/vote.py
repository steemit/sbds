# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Integer, Enum

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class VoteOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
    "ref_block_prefix": 286809142,
    "expiration": "2016-12-16T11:31:55",
    "operations": [
        [
            "vote",
            {
                "voter": "a00",
                "weight": 10000,
                "author": "kibbjez",
                "permlink": "t6wv1"
            }
        ]
    ],
    "signatures": [
        "20795b036ba95df0b211bc6e79c3a1d0c2363e694aee62e79eeb60f5ed859d21b86dc2205f28e8779d369a8e9a1c898df0e62efbbaf3fc3ae0ac8c8679ed6b2d68"
    ],
    "ref_block_num": 32469,
    "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 11326766,
        "tx_id": 15964182,
        "voter": "a00",
        "author": "kibbjez",
        "permlink": "t6wv1",
        "weight": 10000
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_votes'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    voter = Column(Unicode(50), nullable=False, index=True)
    author = Column(Unicode(50), nullable=False, index=True)
    permlink = Column(Unicode(512), nullable=False)
    weight = Column(Integer)

    _fields = dict(
        voter=lambda x: x.get('voter'),
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        weight=lambda x: x.get('weight')
    )


    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

