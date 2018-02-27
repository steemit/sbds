# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import SmallInteger
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from toolz.dicttoolz import dissoc

import sbds.sbds_json
import structlog

from ...query_helpers import standard_trailing_windows
from ...utils import UniqueMixin
from ..core import extract_operations_from_block


logger = structlog.get_logger(__name__)


class UndefinedTransactionType(Exception):
    """Exception raised when undefined transction is encountered"""


# noinspection PyMethodParameters
class OperationMixin(UniqueMixin):

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return tuple([
            kwargs['block_num'], kwargs['transaction_num'],
            kwargs['operation_num']
        ])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(
            cls.block_num == kwargs['block_num'],
            cls.transaction_num == kwargs['transaction_num'],
            cls.operation_num == kwargs['operation_num'], )

    # pylint: enable=unused-argument

    def dump(self):
        return dissoc(self.__dict__, '_sa_instance_state')

    def to_dict(self, decode_json=True):
        data_dict = self.dump()
        if isinstance(data_dict.get('json_metadata'), str) and decode_json:
            data_dict['json_metadata'] = sbds.sbds_json.loads(
                data_dict['json_metadata'])
        return data_dict

    def to_json(self):
        data_dict = self.to_dict()
        return sbds.sbds_json.dumps(data_dict)

    def __repr__(self):
        return "<%s (block_num:%s transaction_num: %s operation_num: %s keys: %s)>" % (
            self.__class__.__name__, self.block_num, self.transaction_num,
            self.operation_num, tuple(self.dump().keys()))

    def __str__(self):
        return str(self.dump())

# noinspection PyMethodParameters


class BaseOperation(OperationMixin):
    # pylint: disable=no-self-argument

    @declared_attr
    def __table_args__(cls):
        args = (PrimaryKeyConstraint('block_num', 'transaction_num',
                                     'operation_num'),)
        return getattr(cls, '__extra_table_args__', tuple()) + args

    # pylint: enable=no-self-argument

    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    trx_id = Column(String(40), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=False), index=True)

    _fields = dict()


class BaseVirtualOperation(OperationMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, default=0)
    operation_num = Column(SmallInteger, default=0)
    trx_id = Column(String(40), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=False), nullable=False, index=True)

    _fields = dict()
