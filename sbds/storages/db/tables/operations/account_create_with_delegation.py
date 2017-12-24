# coding=utf-8

import os.path


from sqlalchemy import Column, Numeric, Unicode, UnicodeText, Enum
from toolz import get_in

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation

from .. import Base
from ...field_handlers import amount_field

class AccountCreateWithDelegationOperation(Base, BaseOperation):
    """


    Args:

    Returns:

    """

    __tablename__ = 'sbds_op_account_create_with_delegations'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    fee = Column(Numeric(15, 6), nullable=False)
    delegation = Column(Numeric(15, 6), nullable=False)
    creator = Column(Unicode(50), nullable=False, index=True)
    new_account_name = Column(Unicode(50), index=True)
    owner_key = Column(Unicode(80), nullable=False)
    active_key = Column(Unicode(80), nullable=False)
    posting_key = Column(Unicode(80), nullable=False)
    memo_key = Column(Unicode(250), nullable=False)
    json_metadata = Column(UnicodeText)

    _fields = dict(
        fee=lambda x: amount_field(x.get('fee'), num_func=float),
        delegation=lambda x: amount_field(x.get('delegation'), num_func=float),
        creator=lambda x: x.get('creator'),
        new_account_name=lambda x: x.get('new_account_name'),
        owner_key=lambda x: get_in(['owner', 'key_auths', 0, 0], x),
        active_key=lambda x: get_in(['active', 'key_auths', 0, 0], x),
        posting_key=lambda x: get_in(['posting', 'key_auths', 0, 0], x),
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'))
    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

