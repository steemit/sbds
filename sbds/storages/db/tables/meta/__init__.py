# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship

from sbds.storages.db.tables import Base
from sbds.storages.db.utils import UniqueMixin


class Account(Base, UniqueMixin):
    """Steem Account Meta Class

    """

    __tablename__ = 'sbds_meta_accounts'
    name = Column(String(50), primary_key=True)
    child = relationship("Child", backref="parents")
