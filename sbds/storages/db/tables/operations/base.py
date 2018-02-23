# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
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
    # pylint: disable=no-self-argument

    @classmethod
    def _prepare_for_storage(cls, **kwargs):
        data_dict, _fields = dict(), dict()
        op_type = None
        from sbds.storages.db.tables.operations import tx_class_for_type
        try:
            data_dict = kwargs['data_dict']
            op_type = data_dict['type']
            tx_cls = tx_class_for_type(op_type)
            _fields = tx_cls._fields
            prepared = {k: v(data_dict) for k, v in _fields.items()}
            prepared['block_num'] = data_dict['block_num']
            prepared['transaction_num'] = data_dict['transaction_num']
            prepared['operation_num'] = data_dict['operation_num']
            prepared['timestamp'] = data_dict['timestamp']
            prepared['operation_type'] = op_type

            if 'class_tuple' in kwargs:
                return tx_cls, prepared
            return prepared

        except Exception as e:
            extra = dict(
                block_num=data_dict.get('block_num'),
                transaction_num=data_dict.get('transaction_num'),
                operation_num=data_dict.get('operation_num'),
                timestamp=data_dict.get('timestamp'),
                op_type=op_type,
                _fields=_fields,
                error=e,
                **kwargs)
            logger.error(e, **extra)
            return None

    @classmethod
    def from_raw_block(cls, raw_block):
        from sbds.storages.db.tables.operations import tx_class_for_type
        operations = list(extract_operations_from_block(raw_block))
        if not operations:
            # root_logger.debug('no transactions extracted from block')
            return []

        bn = operations[0].get('block_num', '')
        logger.debug('extracted %s operations from block %s',
                     len(operations), bn)
        prepared = [cls._prepare_for_storage(data_dict=d) for d in operations]
        objs = []
        for i, prepared_tx in enumerate(prepared):
            op_type = operations[i]['type']
            try:
                tx_cls = tx_class_for_type(op_type)
            except UndefinedTransactionType as e:
                logger.error(e)
                continue
            else:
                logger.debug('operation type %s mapped to class %s', op_type,
                             tx_cls.__name__)
                objs.append(tx_cls(**prepared_tx))
                logger.debug('instantiated: %s',
                             [o.__class__.__name__ for o in objs])
        return objs



    # pylint: disable=unused-argument
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
    timestamp = Column(DateTime(timezone=False), index=True)

    _fields = dict()



class BaseVirtualOperation(OperationMixin):

    id = Column(Integer, primary_key=True, autoincrement=True)
    block_num = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=False), nullable=False, index=True)

    _fields = dict()

