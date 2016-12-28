# -*- coding: utf-8 -*-
from collections import namedtuple

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.sql import select
from sqlalchemy.sql import func
from sqlalchemy.sql import exists

'''
CREATE TABLE IF NOT EXISTS Transactions (
    tx_id integer NOT NULL auto_increment,
    block_num integer NOT NULL, # block_num of block where tranasaction was published
    transaction_num smallint NOT NULL, # 1-based index of transactions array in block
    ref_block_num integer NOT NULL, # block_num -1 ?
    ref_block_prefix bigint NOT NULL, ?
    expiration datetime NOT NULL,
    type varchar(50) NOT NULL,
    PRIMARY KEY (tx_id)
)
'''

'''
single transaction
==================
{
    "expiration": "2016-12-19T17:11:21",
    "extensions": [],
    "operations": [
        ["vote", {
            "voter": "intelliguy",
            "author": "trevor.george",
            "weight": 10000,
            "permlink": "what-is-it-about-steemit-that-sets-it-apart-from-other-blogging-platforms"}
        ]
    ],
    "signatures": [
        "20650caa0464a35f83e7a1a7e5ce28914eb179dd4edada3650f6ca5df16d0d2d9160c61c62c22ccf43a780ed90ababf1fb49bffdb0d095024e2a27b2c3549ff553"
    ],
    "ref_block_num": 59862,
    "ref_block_prefix": 4197255167
}
'''

tx_types = {
    'account_create':'TxAccountCreates',
    'account_update':'TxAccountUpdates',
    'account_witness_proxy':'TxAccountWitnessProxies',
    'account_witness_vote':'TxAccountWitnessVotes',
    'cancel_transfer_from_savings':None,
    'change_recovery_account':'TxAccountUpdates',
    'comment':'TxComments',
    'comment_options':'TxCommentOptions',
    'convert':'TxConverts',
    'custom':'TxCustoms',
    'custom_json':None,
    'delete_comment':'TxDeleteComments',
    'feed_publish':'TxFeeds',
    'limit_order_cancel':'TxLimitOrders',
    'limit_order_create':'TxLimitOrders',
    'pow':'TxPows',
    'pow2':'TxPows',
    'recover_account':'TxAccountRecovers',
    'request_account_recovery':'TxAccountRecovers',
    'set_withdraw_vesting_route':'TxWithdrawVestingRoutes',
    'transfer':'TxTransfers',
    'transfer_from_savings':'TxTransfers',
    'transfer_to_savings':'TxTransfers',
    'transfer_to_vesting':'TxTransfers',
    'vote':'TxVotes',
    'withdraw_vesting':None,
    'witness_update':'TxWintessUpdates'
}


DATABASE_URL = 'mysql+mysqldb://root:ejokyibbsgc9way@dev-1.c5fwsnh29c0p.us-east-1.rds.amazonaws.com/steem'

DbBlock = namedtuple('Block',['raw','block_num','previous','timestamp','witness','witness_signature',
                            'transaction_merkle_root','extentions','transactions'])
BlockTransaction = namedtuple('BlockTransaction',['block_num','tx_idx','transaction'])

DbTransaction = namedtuple('DbTransaction',['block_num', 'transaction_num', 'ref_block_num', 'ref_block_prefix',
                                            'expiration', 'type'])


class BaseSQLClass(object):
    def __init__(self, engine, table_name=None, chunksize=10000, execution_options=None, pk=None):
        self.engine = engine
        self.meta = MetaData()
        self.meta.reflect(bind=self.engine)
        self.table = self.meta.tables[table_name]
        self.execution_options = execution_options or dict(stream_results=True)
        self.chunksize = 10000
        self.pk = pk or list(self.table.primary_key.columns)[0]


    def iter_result(self, stmt):
        with self.engine.connect() as conn:
            result = conn.execute(stmt, execution_options=self.execution_options)
            while True:
                chunk = result.fetchmany(self.chunksize)
                if not chunk:
                    break
                for block in chunk:
                    yield block
            result.close()

    def __iter__(self):
        stmt = self.table.select()
        return self.iter_result(stmt)

    def __reversed__(self):
        stmt = self.table.select().order_by('{} DESC'.format(self.pk.name))
        return self.iter_result(stmt)

    def __contains__(self, key):
        return self.conn.scalar(select([exists().where(self.pk == key)]))


    def __getitem__(self, item):
        if isinstance(item, int):
            stmt = self.table.select().where(self.pk == item)
            result = self.conn.execute(stmt)
            item = result.first()
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
            return self.iter_result(stmt)

    def __setitem__(self, key, value):
        stmt = self.table.insert(raw=value)
        result = self.conn.execute(stmt)
        result.close()

    def __delitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        return self.conn.scalar(select([func.count(self.pk)]).select_from(self.table))



class Blocks(BaseSQLClass):
    def __init__(self, *args, **kwargs):
        kwargs['table_name'] = kwargs.get('table_name') or 'Blocks'
        super(Blocks, self).__init__(*args, **kwargs)

    def append(self, block):
        with self.engine.connect() as conn:
            stmt = self.table.insert(raw=block)
            result = conn.execute(stmt)

class Transactions(BaseSQLClass):
    def __init__(self, *args, **kwargs):
        kwargs['table_name'] = kwargs.get('table_name') or 'Transactions'
        super(Transactions, self).__init__(*args, **kwargs)

    def append(self, transaction):
        with self.engine.connect() as conn:
            stmt = self.table.insert()


def transactions_from_blocks(blocks):
    for block in blocks:
        for tx_idx, transaction in enumerate(block[1], 1):
            yield DbTransaction(block_num=block[0], transaction_num=tx_idx,
                                   ref_block_num=transaction['ref_block_num'],
                                   ref_block_prefix=transaction['ref_block_prefix'],
                                   expiration=transaction['expiration'],
                                   type=transaction['operations'][0][0])

def insert_transactions(self, transactions, chunk_size=10000):
    conn = self.connect()
    for chunk in chunks(transactions, chunk_size):
        conn.execute(self.tx_table.insert(), [t._asdict() for t in chunk])
