# -*- coding: utf-8 -*-
from itertools import chain
import ujson as json

import dateutil.parser
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists
from sqlalchemy.sql import select
from sqlalchemy.sql import func

import sbds.logging
from sbds.storages import AbstractStorageContainer
from sbds.storages.db.tables import blocks_table
from sbds.storages.db.tables import transactions_table
from sbds.utils import block_num_from_previous, chunkify

logger = sbds.logging.getLogger(__name__)

tx_types = {
    'account_create': 'TxAccountCreates',
    'account_update': 'TxAccountUpdates',
    'account_witness_proxy': 'TxAccountWitnessProxies',
    'account_witness_vote': 'TxAccountWitnessVotes',
    'cancel_transfer_from_savings': None,
    'change_recovery_account': 'TxAccountUpdates',
    'comment': 'TxComments',
    'comment_options': 'TxCommentOptions',
    'convert': 'TxConverts',
    'custom': 'TxCustoms',
    'custom_json': None,
    'delete_comment': 'TxDeleteComments',
    'feed_publish': 'TxFeeds',
    'limit_order_cancel': 'TxLimitOrders',
    'limit_order_create': 'TxLimitOrders',
    'pow': 'TxPows',
    'pow2': 'TxPows',
    'recover_account': 'TxAccountRecovers',
    'request_account_recovery': 'TxAccountRecovers',
    'set_withdraw_vesting_route': 'TxWithdrawVestingRoutes',
    'transfer': 'TxTransfers',
    'transfer_from_savings': 'TxTransfers',
    'transfer_to_savings': 'TxTransfers',
    'transfer_to_vesting': 'TxTransfers',
    'vote': 'TxVotes',
    'withdraw_vesting': None,
    'witness_update': 'TxWitnessUpdates'
}


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

    def add_many(self, items, chunksize=1000, retry_skipped=False, raise_on_error=True):
        skipped = []
        added_count = 0
        with self.engine.connect() as conn:
            for i, chunk in enumerate(chunkify(items, chunksize), 1):
                kv_pairs = [self._prepare_for_storage(None, item) for item in chunk]
                values = [v[1] for v in kv_pairs]
                extra = dict(chunk_count=i, values_count=len(values),
                             skipped_item_count=len(skipped), added_item_count=added_count)
                logger.debug('adding chunk of %ss', self.name, extra=extra)
                try:
                    conn.execute(self.table.insert(), values)
                    added_count += len(values)
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
                    added_count, len(skipped), self.name)
        if not retry_skipped or len(skipped) == 0:
            return added_count, skipped

        with self.engine.connect() as conn:
            logger.info('retrying to add %s skipped %ss', len(skipped), self.name)
            for i, item in enumerate(skipped):
                try:
                    self.add(item, prepared=True)
                    added_count += 1
                    del skipped[i]
                except Exception as e:
                    extra=dict(item_type=self.name,
                               block_num=item['block_num'],
                               error=e)
                    logger.error('Error while retrying skipped %s', self.name, extra=extra)

        return added_count, skipped

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
        kwargs['table'] = blocks_table
        kwargs['name'] = 'block'
        super(Blocks, self).__init__(*args, **kwargs)

    @property
    def pk(self):
        return self.table.c['block_num']

    def _prepare_for_storage(self, block_num, block):
        raw = None
        if not isinstance(block, dict):
            raw = block
            block_dict = json.loads(block)
        else:
            block_dict = block
        if not block_dict.get('raw'):
            raw = raw or json.dumps(block_dict, ensure_ascii=True).encode('utf8')
            block_dict.update(raw=raw)
        block_num = block_num_from_previous(block_dict['previous'])
        block_dict.update(block_num=block_num)
        return block_dict['block_num'], block_dict

    @property
    def block_nums(self):
        stmt = select([self.table.c.block_num])
        result = self._execute_iter(stmt)
        return (row[0] for row in result)

    def missing(self, block_height=None):
        block_height = block_height or len(self)
        existing_block_nums = frozenset(self.block_nums)
        return frozenset(range(1, block_height)) -  existing_block_nums

    def get_blocks_with_transactions(self, block_num_only=False, transactions_only=False):
        c = self.table.c
        if block_num_only:
            stmt = select([c.block_num]).where(func.LENGTH(c.transactions) > 10)
            result = self._execute_iter(stmt)
            return (b[0] for b in result)
        elif transactions_only:
            stmt = select([c.block_num, c.transactions]).where(func.LENGTH(c.transactions) > 10)
            result = self._execute_iter(stmt)
            for block_num, transaction_txt in result:
                transactions = json.loads(transaction_txt)
                for transaction in transactions:
                    transaction['block_num'] = block_num
                    yield transaction
        else:
            stmt = self.table.select().where(func.LENGTH(c.transactions) > 10)
            return self._execute_iter(stmt)

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
        return self.table.c['txid']

    def __delitem__(self, key):
        pass

    def __eq__(self):
        pass

def extract_transactions_from_blocks(blocks):
    transactions = chain.from_iterable(map(extract_transactions_from_block, blocks))
    return transactions

def extract_transactions_from_block(block):
    if isinstance(block, (str, bytes)):
        try:
            block = json.loads(block)
        except ValueError as e:
            extra = dict(block=block, error=e)
            logger.error('Unable load json block', extra=extra)
            raise e
    block_num = block.get('block_num', block_num_from_previous(block['previous']))
    for transaction_num, t in enumerate(block['transactions']):
        yield dict(block_num=block_num,
                   transaction_num=transaction_num,
                   ref_block_num=t['ref_block_num'],
                   ref_block_prefix=t['ref_block_prefix'],
                   expiration=t['expiration'],
                   type=t['operations'][0][0],
                   operations=t['operations'],
                   op_count=len(t['operations']))

def is_duplicate_entry_error(error):
    try:
        return "Duplicate entry" in str(error.orig)
    except Exception as e:
        logger.exception(e)
        return False

