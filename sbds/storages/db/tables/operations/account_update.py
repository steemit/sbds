# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class AccountUpdateOperation(Base, BaseOperation):
    """Raw Format
    {
        "memo_key": "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
        "active": {
            "account_auths": [],
            "weight_threshold": 1,
            "key_auths": [
                [
                    "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
                    1
                ],
                [
                    "STM76EQNV2RTA6yF9TnBvGSV71mW7eW36MM7XQp24JxdoArTfKA76",
                    1
                ]
            ]
        },
        "account": "theoretical",
        "json_metadata": ""
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_account_updates'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    account = Column(Unicode(50))
    key_auth1 = Column(Unicode(80))
    key_auth2 = Column(Unicode(80))
    memo_key = Column(Unicode(250))
    json_metadata = Column(UnicodeText)

    _fields = dict(
        account=lambda x: x.get('account'),
        key_auth1=lambda x: None,  # TODO fix null
        key_auth2=lambda x: None,  # TODO fix null
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
