# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime


from sbds.storages.db.tables import Base
from sbds.storages.db.utils import UniqueMixin


class AccountEvents(Base):
    """Steem Account Events Meta Class

    """
    timestamp = Column(DateTime)
    block_num = Column(Integer)
    transaction_num = Column(Integer)
    operation_num = Column(Integer)
    operation_type = Column(String)
    field_name = Column(String)
    account = Column(String(16))
