# -*- coding: utf-8 -*-

import dateutil.parser
import rapidjson

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean
from sqlalchemy import SmallInteger
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import JSONB

from ..import Base
from ...enums import operation_types_enum
from ...field_handlers import json_string_field
from ...field_handlers import amount_field
from ...field_handlers import amount_symbol_field
from ...field_handlers import comment_body_field
from .base import BaseOperation
from .base import BaseVirtualOperation

class SetWithdrawVestingRouteOperation(Base, BaseOperation):
    """


    Steem Blockchain Example
    ======================
    {
      "percent": 10000,
      "to_account": "newyo",
      "auto_vest": true,
      "from_account": "newyo6"
    }



    """

    __tablename__ = 'sbds_op_set_withdraw_vesting_routes'
    __operation_type__ = 'set_withdraw_vesting_route_operation'

    from_account = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    to_account = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:account_name_type
    percent = Column(Integer) # steem_type:uint16_t
    auto_vest = Column(Boolean) # steem_type:bool
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='set_withdraw_vesting_route')

    _fields = dict(

    )


