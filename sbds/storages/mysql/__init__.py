# -*- coding: utf-8 -*-
import json
from collections import namedtuple

from sqlalchemy.sql import exists
from sqlalchemy.sql import select

from sbds.storages.mysql.tables import blocks_table
from sbds.storages.mysql.tables import transactions_table
from sbds.utils import block_num_from_previous

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
    'witness_update': 'TxWintessUpdates'
}


class BaseSQLClass(object):
    def __init__(self, engine=None, table=None, chunksize=10000, execution_options=None):
        self.engine = engine
        self.table = table
        self.table_name = self.table.name
        self.meta = self.table.metadata
        self.execution_options = execution_options or dict(stream_results=True)
        self.chunksize = 10000

    @property
    def pk(self):
        raise NotImplementedError

    def _execute(self, stmt):
        with self.engine.connect() as conn:
            return conn.execute(stmt)

    def _first(self, stmt):
        with self.engine.connect() as conn:
            return conn.execute(stmt).first()

    def _scalar(self, stmt):
        with self.engine.connect() as conn:
            return conn.scalar(stmt)

    def _prepare_for_storage(self, item):
        return item

    @property
    def _engine_config_dict(self):
        return self.engine.url.__dict__

    def _execute_iter(self, stmt):
        with self.engine.connect() as conn:
            result = conn.execute(stmt, execution_options=self.execution_options)
            while True:
                chunk = result.fetchmany(self.chunksize)
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
            stmt = self.table.select(limit=item.stop - 1, offset=item.start)
            return self._execute_iter(stmt)

    def __setitem__(self, key, value):
        data = self._prepare_for_storage(key, value)
        with self.engine.connect() as conn:
            return conn.execute(self.table.insert(), **data)

    def __delitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        stmt = 'SELECT n_rows FROM mysql.innodb_table_stats WHERE TABLE_NAME ="{}"'.format(self.table_name)
        return self._scalar(stmt)


class Blocks(BaseSQLClass):
    def __init__(self, *args, **kwargs):
        kwargs['table'] = blocks_table
        super(Blocks, self).__init__(*args, **kwargs)

    @property
    def pk(self):
        return self.table.c['block_num']

    def _prepare_for_storage(self, block_num, block):
        block_dict = json.loads(block)
        block_num = block_num_from_previous(block_dict['previous'])
        block_dict.update(raw=block, block_num=block_num)
        return block_dict

    @property
    def block_nums(self):
        stmt = select([self.table.c.block_num])
        result = self._execute(stmt)
        nums = result.fetchall()
        return (n[0] for n in nums)

    def missing(self):
        return frozenset(range(1, len(self))) - frozenset(self.block_nums)

    def __len__(self):
        stmt = 'SELECT MAX({}) FROM {}'.format(self.pk.name, self.table.name)
        return self._scalar(stmt)


class Transactions(BaseSQLClass):
    def __init__(self, *args, **kwargs):
        kwargs['table'] = transactions_table
        super(Transactions, self).__init__(*args, **kwargs)

    @property
    def pk(self):
        return self.table.c['block_num']
