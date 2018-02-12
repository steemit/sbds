# coding=utf-8

import os.path

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from ...field_handlers import amount_field
from .base import BaseOperation


class CommentOptionOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 3739556666,
        "expiration": "2016-08-12T07:02:19",
        "operations": [
            [
                "comment_options",
                {
                    "author": "testing001",
                    "allow_curation_rewards": true,
                    "max_accepted_payout": "1000.000 SBD",
                    "percent_steem_dollars": 5000,
                    "allow_votes": true,
                    "permlink": "testing6",
                    "extensions": []
                }
            ]
        ],
        "signatures": [
            "1f47ff6711fad1ab07a9e10ce91e1fd84ca49629a6f45af6aca67150705e651b2006b5548520995bedd09daf6f597d2bc68a30c7c161b4600e14f0032e69235fcf"
        ],
        "ref_block_num": 13118,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 1,
        "tx_id": 3924992,
        "author": "testing001",
        "permlink": "testing6",
        "max_accepted_payout": 1000.0000,
        "percent_steem_dollars": 5000,
        "allow_votes": True,
        "allow_curation_rewards": True
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_comments_options'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    author = Column(Unicode(50), nullable=False)
    permlink = Column(Unicode(512), nullable=False)
    max_accepted_payout = Column(Numeric(15, 6), nullable=False)
    percent_steem_dollars = Column(SmallInteger, default=0)
    allow_votes = Column(Boolean, nullable=False)
    allow_curation_rewards = Column(Boolean, nullable=False)

    _fields = dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        max_accepted_payout=lambda x: amount_field(x.get('max_accepted_payout'), num_func=float),
        percent_steem_dollars=lambda x: x.get('percent_steem_dollars'),
        allow_votes=lambda x: x.get('allow_votes'),
        allow_curation_rewards=lambda x: x.get('allow_curation_rewards'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
