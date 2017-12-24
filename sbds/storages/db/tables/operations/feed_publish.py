# coding=utf-8

import os.path


from sqlalchemy import Column, Unicode, Numeric, Enum
from toolz import get_in

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class FeedPublishOperation(Base, BaseOperation):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 336265640,
        "expiration": "2016-04-26T23:08:06",
        "operations": [
            [
                "feed_publish",
                {
                    "exchange_rate": {
                        "quote": "1.000 STEEM",
                        "base": "0.374 SBD"
                    },
                    "publisher": "smooth.witness"
                }
            ]
        ],
        "signatures": [
            "1f45f20c78e105eba93946b4366293f28a1d5b5e6e52e2007e8c0965c19bdd5b1464ba7a6b274d1a483715e3a883125106905c24e57092bc89247689cdc335c3fc"
        ],
        "ref_block_num": 19946,
        "extensions": []
    }


    Prepared Format
    ===============
    {
        "id": 23,
        "tx_id": 157612,
        "publisher": "smooth.witness",
        "exchange_rate_base": 0.3740,
        "exchange_rate_quote": 1.0000
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_feed_publishes'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    publisher = Column(Unicode(50), nullable=False)
    exchange_rate_base = Column(Numeric(15, 6), nullable=False)
    exchange_rate_quote = Column(Numeric(15, 6), nullable=False)

    _fields = dict(
     publisher=lambda x: x.get('publisher'),
        exchange_rate_base=lambda x: amount_field(
            get_in(['exchange_rate', 'base'], x), num_func=float),
        exchange_rate_quote=lambda x: amount_field(
            get_in(['exchange_rate', 'quote'], x), num_func=float)
    )


    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

