# coding=utf-8

import os.path

from sqlalchemy import Column
from sqlalchemy import Unicode

from .. import Base
from ...enums import operation_types_enum
from .base import BaseOperation


class ChangeRecoveryAccountOperation(Base, BaseOperation):
    """Raw Format
    ==========

    {
        "account_to_recover": "barrie",
        "extensions": [],
        "new_recovery_account": "boombastic"
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_change_recovery_accounts'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    account_to_recover = Column(Unicode(50))
    new_recovery_account = Column(Unicode(50))

    _fields = dict(
        account_to_recover=lambda x: x.get('account_to_recover'),
        new_recovery_account=lambda x: x.get('new_recovery_account'))

    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default=__operation_type__)
