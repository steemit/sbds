# coding=utf-8
from functools import partial

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import Table

from toolz import dissoc


from sbds.storages.db.tables import Base
from sbds.storages.db.utils import UniqueMixin


association_table = Table('association', Base.metadata,
    Column('left_account', Integer, ForeignKey('account.id')),
    Column('key', Integer, ForeignKey('right.id'))
)

class Key(Base, UniqueMixin):
    """
    """
    # pylint: enable=line-too-long
    __tablename__ = 'sbds_extra_keys'
    __table_args__ = ({
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }, )

    key = Column(Unicode(100), primary_key=True)

    def __repr__(self):
        return "<Key(%s)>" % self.key





