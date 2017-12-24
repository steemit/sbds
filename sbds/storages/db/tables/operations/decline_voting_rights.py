# coding=utf-8

import os.path


import os.path
from sqlalchemy import Column, Unicode, Boolean, Enum

from ...field_handlers import amount_field
from ...enums import operation_types_enum
from .. import Base
from .base import BaseOperation



class DeclineVotingRightsOperation(Base, BaseOperation):

    __tablename__ = 'sbds_op_decline_voting_rights'
    __operation_type__ = os.path.splitext(os.path.basename(__file__))[0]

    account = Column(Unicode(50), nullable=False)
    decline = Column(Boolean, default=True)

    _fields = dict(
        account=lambda x: x.get('account'),
        decline=lambda x: x.get('decline'))

    operation_type = Column(operation_types_enum, nullable=False, index=True, default=__operation_type__)

