# -*- coding: utf-8 -*-

from itertools import chain
from copy import deepcopy
from copy import copy

from collections import defaultdict

import ujson as json

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists
from sqlalchemy.sql import select

import sbds.logging
from sbds.storages import AbstractStorageContainer

#from sbds.storages.db.tables import blocks_table
#from sbds.storages.db.tables import transactions_table
#from sbds.storages.db.tables import transactions_table as operations_table

from sbds.utils import block_num_from_previous, chunkify

logger = sbds.logging.getLogger(__name__)


class BaseSQLClass(AbstractStorageContainer):
    def __init__(self, engine=None, table=None, chunksize=10000, execution_options=None, name='item', **kwargs):
        self.engine = engine
        self.table = table
        self.table_name = self.table.name
        self.meta = self.table.metadata
        self.execution_options = execution_options or dict(stream_results=True)
        self.chunksize = chunksize
        self.name = name
        super(BaseSQLClass, self).__init__(**kwargs)

    @property
    def pk(self):
        raise NotImplementedError

    def _execute(self, stmt, *args, **kwargs):
        with self.engine.connect() as conn:
            return conn.execute(stmt, *args, **kwargs)

    def _first(self, stmt):
        with self.engine.connect() as conn:
            return conn.execute(stmt).first()

    def _scalar(self, stmt):
        with self.engine.connect() as conn:
            return conn.scalar(stmt)

    def _prepare_for_storage(self, key, value):
        return key, value

    @property
    def _engine_config_dict(self):
        return self.engine.url.__dict__

    def _execute_iter(self, stmt, chunksize=None):
        chunksize = chunksize or self.chunksize
        with self.engine.connect() as conn:
            result = conn.execute(stmt, execution_options=self.execution_options)
            while True:
                chunk = result.fetchmany(chunksize)
                if not chunk:
                    break
                for block in chunk:
                    yield block

    def __iter__(self):
        stmt = self.table.select()
        return self._execute_iter(stmt)

    def __reversed__(self):
        stmt = self.table.select().order_by('{} DESC'.format(self.pk.name))
        return self._execute_iter(stmt)

    def __contains__(self, key):
        stmt = select([exists().where(self.pk == key)])
        return self._scalar(stmt)

    def __getitem__(self, item):
        if isinstance(item, int):
            stmt = self.table.select().where(self.pk == item)
            item = self._first(stmt)
            if not item:
                raise KeyError
            else:
                return item
        else:
            if item.step and item.step is not 1:
                raise NotImplementedError('Slice step must be 1')
            if item.stop:
                limit = item.stop - 1
            else:
                limit = None
            stmt = self.table.select(limit=limit, offset=item.start)
            return self._execute_iter(stmt)

    def __setitem__(self, key, value):
        key, value = self._prepare_for_storage(key, value)
        with self.engine.connect() as conn:
            try:
                return conn.execute(self.table.insert(), **value)
            # handle existing value
            except IntegrityError as e:
                self.handle_integrity_error(e)
                extra = dict(key=key, value=value)
            except Exception as e:
                extra = dict(key=key, value=value, error=e)
                logger.error('Unable to __setitem__', extra=extra)
                raise e

    def __delitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        stmt = 'SELECT MAX({}) FROM {}'.format(self.pk.name, self.table.name)
        return self._scalar(stmt) or 0

    def __str__(self):
        return json.dumps(self, ensure_ascii=True).encode('utf8')

    def add(self, item, prepared=False):
        if not prepared:
            self.__setitem__(None, item)
            return
        with self.engine.connect() as conn:
            try:
                conn.execute(self.table.insert(), **item)
            except IntegrityError as e:
                self.handle_integrity_error(e)

    def add_many(self, items, chunksize=1000, raise_on_error=True):
        skipped = []
        added = []

        with self.engine.connect() as conn:
            for i, chunk in enumerate(chunkify(items, chunksize), 1):

                kv_pairs = [self._prepare_for_storage(None, item) for item in chunk]

                values = [v[1] for v in kv_pairs]
                extra = dict(chunk_count=i, values_count=len(values),
                             skipped_item_count=len(skipped), added_item_count=added)

                logger.debug('adding chunk of %ss', self.name, extra=extra)

                try:
                    conn.execute(self.table.insert(), values)
                    added.extend(values)

                except IntegrityError as e:
                    extra = dict(skipped_item_count=len(skipped), chunksize=chunksize)
                    logger.debug('add_many IntegrityError, adding chunk to skipped %s', self.name, extra=extra)
                    skipped.extend(values)

                except Exception as e:
                    skipped.extend(values)
                    logger.exception(e)
                    if raise_on_error:
                        raise(e)

        logger.info('add_many results: added %s, skipped %s %ss',
                    len(added), len(skipped), self.name)

    @staticmethod
    def handle_integrity_error(e):
        if not is_duplicate_entry_error(e):
            extra = dict(error=e)
            logger.error('Non duplicate entry IntegrityError', extra=extra)
            raise e

    def __hash__(self):
        pass

    def __eq__(self):
        pass


class Blocks(BaseSQLClass):
    def __init__(self, *args, **kwargs):
        #kwargs['table'] = blocks_table
        kwargs['name'] = 'block'
        super(Blocks, self).__init__(*args, **kwargs)

    @property
    def pk(self):
        return self.table.c['block_num']

    def _prepare_for_storage(self, block_num, block):
        block_dict = self.prepare(block)
        return block_dict['block_num'], block_dict

    def prepare(self, block):
        raw = None
        if not isinstance(block, dict):
            raw = block
            block_dict = json.loads(block)
        else:
            block_dict = block
        if not block_dict.get('raw'):
            raw = raw or json.dumps(block_dict, ensure_ascii=True).encode('utf8')
            block_dict.update(raw=raw)
        elif isinstance(block_dict['raw'], bytes):
            block_dict['raw'] = block_dict['raw'].decode('utf8')
        block_num = block_num_from_previous(block_dict['previous'])
        block_dict.update(block_num=block_num)
        return block_dict

    @property
    def block_nums(self):
        stmt = select([self.table.c.block_num])
        result = self._execute_iter(stmt)
        return (row[0] for row in result)

    def missing(self, block_height=None):
        block_height = block_height or len(self)
        existing_block_nums = frozenset(self.block_nums)
        return frozenset(range(1, block_height)) -  existing_block_nums

    def __delitem__(self, key):
        pass

    def __eq__(self):
        pass


class Transactions(BaseSQLClass):
    def __init__(self, *args, **kwargs):
        kwargs['table'] = transactions_table
        kwargs['name'] = 'transaction'
        super(Transactions, self).__init__(*args, **kwargs)

    @property
    def pk(self):
        return self.table.c['tx_id']

    def __delitem__(self, key):
        pass

    def __eq__(self):
        pass



def prepare_raw_block(raw_block):
    block_dict = dict()
    if isinstance(raw_block, dict):
        block = deepcopy(raw_block)
        block_dict.update(**block)
        block_dict['raw'] = json.dumps(block, ensure_ascii=True)
    elif isinstance(raw_block, str):
        block_dict.update(**json.loads(raw_block))
        block_dict['raw'] = copy(raw_block)
    elif isinstance(raw_block, bytes):
        block = deepcopy(raw_block)
        raw = block.decode('utf8')
        block_dict.update(**json.loads(raw))
        block_dict['raw'] = copy(raw)
    else:
        raise TypeError('Unsupported raw block type')

    block_num = block_num_from_previous(block_dict['previous'])
    block_dict['block_num'] = block_num
    return block_dict


def extract_transactions_from_blocks(blocks):
    transactions = chain.from_iterable(map(extract_transactions_from_block, blocks))
    return transactions


def extract_transactions_from_block(_block):
    block = prepare_raw_block(_block)
    block_transactions = deepcopy(block['transactions'])
    for transaction_num, t in enumerate(block_transactions, 1):
        t = deepcopy(t)
        yield dict(block_num=block['block_num'],
                   transaction_num=transaction_num,
                   ref_block_num=t['ref_block_num'],
                   ref_block_prefix=t['ref_block_prefix'],
                   expiration=t['expiration'],
                   type=t['operations'][0][0],
                   operations=t['operations'])


def extract_operations_from_block(raw_block):
    block = prepare_raw_block(raw_block)

    transactions = extract_transactions_from_block(block)

    for transaction in transactions:
        for op_num, _operation in enumerate(transaction['operations'],1):
            operation = deepcopy(_operation)
            op_type, op = operation
            op.update(
               operation_num=op_num,
               block_num=transaction['block_num'],
               transaction_num=transaction['transaction_num'],
               type=op_type)
            yield op


def extract_operations_from_blocks(blocks):
    operations = chain.from_iterable(map(extract_operations_from_block, blocks))
    return operations


def is_duplicate_entry_error(error):
    try:
        return "duplicate" in str(error.orig).lower()
    except Exception as e:
        extra=dict(exception_type=type(e),exception_dir=dir(e))
        logger.exception(e, extra=extra)
        return False

def add_block(_block):
    pass