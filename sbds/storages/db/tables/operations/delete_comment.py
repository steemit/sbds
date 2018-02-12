# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class DeleteCommentOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 3023139187,
        "expiration": "2016-06-06T19:34:27",
        "operations": [
            [
                "delete_comment",
                {
                    "author": "jsc",
                    "permlink": "tests-delete"
                }
            ]
        ],
        "signatures": [
            "2044602e8a51a6f44827be54fb5fec8b53698fdf608a5fdd5943af71f288229fc078104b9798391989e15153f5f1aeb370d74ec027fefe4b5372a6c90d35b175f3"
        ],
        "ref_block_num": 12211,
        "extensions": []
    }


    Prepared Format
    ===============
    {
        "id": 1,
        "tx_id": 309111,
        "author": "jsc",
        "permlink": "tests-delete"
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_delete_comments'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    author = Column(Unicode(50), nullable=False)
    permlink = Column(Unicode(256), nullable=False)

    _fields = dict(
        author=lambda x: x.get('author'), permlink=lambda x: x.get('permlink'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
