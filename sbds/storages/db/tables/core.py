# -*- coding: utf-8 -*-
import ujson as json
from copy import copy
from copy import deepcopy
from itertools import chain

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import func
import maya

import sbds.logging
from sbds.storages.db.tables import Base
from sbds.storages.db.utils import UniqueMixin
from sbds.utils import block_num_from_previous
from sbds.utils import chunkify

logger = sbds.logging.getLogger(__name__)


class Block(Base, UniqueMixin):
    """
    Raw Format
    ==========
    {
        "extensions": [],
        "timestamp": "2016-08-11T22:00:09",
        "transaction_merkle_root": "57e17f40cfa97c260eef365dc599e06acdba8591",
        "previous": "003d0900c38ca36625f50fc6724cbb9d82a9a93e",
        "witness": "roadscape",
        "transactions": [
            {
                "signatures": [
                    "1f7f99b4e98878ecd2b65bc9e6c8e2fc3a929fdb766411e89b6df2accddf326b901e8bc10c0d0f47738c26c6fdcf15f76a11eb69a12058e96820b2625061d6aa96"
                ],
                "extensions": [],
                "expiration": "2016-08-11T22:00:18",
                "ref_block_num": 2203,
                "operations": [
                    [
                        "comment",
                        {
                            "body": "@@ -154,16 +154,17 @@\n at coffe\n+e\n  deliver\n",
                            "title": "",
                            "author": "mindfreak",
                            "parent_author": "einsteinpotsdam",
                            "permlink": "re-einsteinpotsdam-tutorial-for-other-shop-owners-how-to-accept-steem-and-steem-usd-payments-setup-time-under-2-minutes-android-20160811t215904898z",
                            "parent_permlink": "tutorial-for-other-shop-owners-how-to-accept-steem-and-steem-usd-payments-setup-time-under-2-minutes-android",
                            "json_metadata": "{\"tags\":[\"steemit\"]}"
                        }
                    ]
                ],
                "ref_block_prefix": 3949810370
            },
            {
                "signatures": [],
                "extensions": [],
                "expiration": "2016-08-11T22:00:36",
                "ref_block_num": 2304,
                "operations": [
                    [
                        "witness_update",
                        {
                            "url": "http://fxxk.com",
                            "props": {
                                "maximum_block_size": 65536,
                                "account_creation_fee": "1.000 STEEM",
                                "sbd_interest_rate": 1000
                            },
                            "block_signing_key": "STM5b3wkzd5cPuW8tYbHpsM6qo26R5eympAQsBaoEfeMDxxUCLvsY",
                            "fee": "0.000 STEEM",
                            "owner": "supercomputing06"
                        }
                    ]
                ],
                "ref_block_prefix": 1721994435
            },
            {
                "signatures": [],
                "extensions": [],
                "expiration": "2016-08-11T22:00:36",
                "ref_block_num": 2304,
                "operations": [
                    [
                        "account_update",
                        {
                            "json_metadata": "",
                            "account": "supercomputing06",
                            "memo_key": "STM7myUzFgMrc5w2jRc3LH2cTwcs96q74Kj6GJ3DyKHyrHFPDP96N",
                            "active": {
                                "key_auths": [
                                    [
                                        "STM5sP9GUuExPzK35F1MLjN2dTY7fqqP7dSpMWqnzCoU3je64gm6q",
                                        2
                                    ],
                                    [
                                        "STM7t97bmNzbVruhH3yGQ7yFR58UJyPTb7Jh6ugmPfH1zqzJpngQH",
                                        1
                                    ]
                                ],
                                "weight_threshold": 0,
                                "account_auths": []
                            }
                        }
                    ]
                ],
                "ref_block_prefix": 1721994435
            },
            {
                "signatures": [],
                "extensions": [],
                "expiration": "2016-08-11T22:00:36",
                "ref_block_num": 2304,
                "operations": [
                    [
                        "account_update",
                        {
                            "json_metadata": "",
                            "account": "supercomputing06",
                            "memo_key": "STM7myUzFgMrc5w2jRc3LH2cTwcs96q74Kj6GJ3DyKHyrHFPDP96N",
                            "active": {
                                "key_auths": [
                                    [
                                        "STM5sP9GUuExPzK35F1MLjN2dTY7fqqP7dSpMWqnzCoU3je64gm6q",
                                        2
                                    ],
                                    [
                                        "STM7t97bmNzbVruhH3yGQ7yFR58UJyPTb7Jh6ugmPfH1zqzJpngQH",
                                        1
                                    ]
                                ],
                                "weight_threshold": 2,
                                "account_auths": []
                            }
                        }
                    ]
                ],
                "ref_block_prefix": 1721994435
            }
        ],
        "witness_signature": "20033915d9ddfca226eeadc57807556f18dd1ace85659774f2b6e620c56426e4560449e07635e9724ad1171a1f49800fe392e047e2a69bfbe9ee06948608fca211"
    }

    Prepared Format
    ===============
    {
        "block_num": 4000001,
        "previous": "003d0900c38ca36625f50fc6724cbb9d82a9a93e",
        "timestamp": "2016-08-11 22:00:09.000",
        "witness": "roadscape",
        "witness_signature": "20033915d9ddfca226eeadc57807556f18dd1ace85659774f2b6e620c56426e4560449e07635e9724ad1171a1f49800fe392e047e2a69bfbe9ee06948608fca211",
        "transaction_merkle_root": "57e17f40cfa97c260eef365dc599e06acdba8591",
        "raw": "{\"previous\":\"003d0900c38ca36625f50fc6724cbb9d82a9a93e\",\"timestamp\":\"2016-08-11T22:00:09\",\"witness\":\"roadscape\",\"transaction_merkle_root\":\"57e17f40cfa97c260eef365dc599e06acdba8591\",\"extensions\":[],\"witness_signature\":\"20033915d9ddfca226eeadc57807556f18dd1ace85659774f2b6e620c56426e4560449e07635e9724ad1171a1f49800fe392e047e2a69bfbe9ee06948608fca211\",\"transactions\":[{\"ref_block_num\":2203,\"ref_block_prefix\":3949810370,\"expiration\":\"2016-08-11T22:00:18\",\"operations\":[[\"comment\",{\"parent_author\":\"einsteinpotsdam\",\"parent_permlink\":\"tutorial-for-other-shop-owners-how-to-accept-steem-and-steem-usd-payments-setup-time-under-2-minutes-android\",\"author\":\"mindfreak\",\"permlink\":\"re-einsteinpotsdam-tutorial-for-other-shop-owners-how-to-accept-steem-and-steem-usd-payments-setup-time-under-2-minutes-android-20160811t215904898z\",\"title\":\"\",\"body\":\"@@ -154,16 +154,17 @@\\n at coffe\\n+e\\n  deliver\\n\",\"json_metadata\":\"{\\\"tags\\\":[\\\"steemit\\\"]}\"}]],\"extensions\":[],\"signatures\":[\"1f7f99b4e98878ecd2b65bc9e6c8e2fc3a929fdb766411e89b6df2accddf326b901e8bc10c0d0f47738c26c6fdcf15f76a11eb69a12058e96820b2625061d6aa96\"]},{\"ref_block_num\":2304,\"ref_block_prefix\":1721994435,\"expiration\":\"2016-08-11T22:00:36\",\"operations\":[[\"witness_update\",{\"owner\":\"supercomputing06\",\"url\":\"http://fxxk.com\",\"block_signing_key\":\"STM5b3wkzd5cPuW8tYbHpsM6qo26R5eympAQsBaoEfeMDxxUCLvsY\",\"props\":{\"account_creation_fee\":\"1.000 STEEM\",\"maximum_block_size\":65536,\"sbd_interest_rate\":1000},\"fee\":\"0.000 STEEM\"}]],\"extensions\":[],\"signatures\":[]},{\"ref_block_num\":2304,\"ref_block_prefix\":1721994435,\"expiration\":\"2016-08-11T22:00:36\",\"operations\":[[\"account_update\",{\"account\":\"supercomputing06\",\"active\":{\"weight_threshold\":0,\"account_auths\":[],\"key_auths\":[[\"STM5sP9GUuExPzK35F1MLjN2dTY7fqqP7dSpMWqnzCoU3je64gm6q\",2],[\"STM7t97bmNzbVruhH3yGQ7yFR58UJyPTb7Jh6ugmPfH1zqzJpngQH\",1]]},\"memo_key\":\"STM7myUzFgMrc5w2jRc3LH2cTwcs96q74Kj6GJ3DyKHyrHFPDP96N\",\"json_metadata\":\"\"}]],\"extensions\":[],\"signatures\":[]},{\"ref_block_num\":2304,\"ref_block_prefix\":1721994435,\"expiration\":\"2016-08-11T22:00:36\",\"operations\":[[\"account_update\",{\"account\":\"supercomputing06\",\"active\":{\"weight_threshold\":2,\"account_auths\":[],\"key_auths\":[[\"STM5sP9GUuExPzK35F1MLjN2dTY7fqqP7dSpMWqnzCoU3je64gm6q\",2],[\"STM7t97bmNzbVruhH3yGQ7yFR58UJyPTb7Jh6ugmPfH1zqzJpngQH\",1]]},\"memo_key\":\"STM7myUzFgMrc5w2jRc3LH2cTwcs96q74Kj6GJ3DyKHyrHFPDP96N\",\"json_metadata\":\"\"}]],\"extensions\":[],\"signatures\":[]}]}"
    }
    """

    __tablename__ = 'sbds_core_blocks'
    __table_args__ = (
        # Index('ix_sbds_core_blocks_raw_fulltext',
        #      'raw', mysql_prefix='FULLTEXT'),
        {
            'mysql_engine' : 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_general_ci'
        },)

    raw = Column(UnicodeText)
    block_num = Column(Integer, primary_key=True, nullable=False,
                       autoincrement=False)
    previous = Column(Unicode(50))
    timestamp = Column(DateTime(timezone=False), index=True)
    witness = Column(Unicode(50))
    witness_signature = Column(Unicode(150))
    transaction_merkle_root = Column(Unicode(50))

    def __repr__(self):
        return "<Block(block_num='%s', timestamp='%s')>" % (
            self.block_num, self.timestamp)

    @classmethod
    def _prepare_for_storage(cls, raw_block):
        block = prepare_raw_block(raw_block)
        return dict(raw=block['raw'],
                    block_num=block['block_num'],
                    previous=block['previous'],
                    timestamp=block['timestamp'],
                    witness=block['witness'],
                    witness_signature=block['witness_signature'],
                    transaction_merkle_root=block['transaction_merkle_root'])

    @classmethod
    def get_or_create_from_raw_block(cls, raw_block, session=None):
        prepared = cls._prepare_for_storage(raw_block)
        return cls.as_unique(session, **prepared)

    @classmethod
    def from_raw_block(cls, raw_block):
        prepared = cls._prepare_for_storage(raw_block)
        return cls(**prepared)

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return kwargs['block_num']

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(cls.block_num == kwargs['block_num'])

    @classmethod
    def highest_block(cls, session):
        return session.query(func.max(cls.block_num)).scalar()

    @classmethod
    def find_missing_iter(cls, session, chunksize=1000):
        query = session.query(cls.block_num).yield_per(chunksize)
        for results in chunkify(query, chunksize):
            block_nums = [r[0] for r in results]
            low = block_nums[0]
            high = block_nums[-1]
            correct = set(range(low, high + 1))
            missing = correct.difference(block_nums)
            yield (low, high, missing)

    @classmethod
    def find_missing(cls, session, chunksize=1000):
        all_missing = []
        for low, high, missing in cls.find_missing_iter(session,
                                                        chunksize=chunksize):
            logger.debug('%s-%s: %s', low, high, len(missing))
            if not missing:
                continue
            old_len = len(all_missing)
            all_missing.extend(missing)
            new_len = len(all_missing)
            logger.debug('extended missing from %s to %s', old_len, new_len)
        return all_missing


def from_raw_block(raw_block, session):
    from .tx import TxBase
    block = Block.get_or_create_from_raw_block(raw_block, session=session)
    tx_transactions = TxBase.from_raw_block(raw_block)
    return block, tx_transactions


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
    if 'block_num' not in block_dict:
        block_num = block_num_from_previous(block_dict['previous'])
        block_dict['block_num'] = block_num
    if isinstance(block_dict.get('timestamp'), str):
        timestamp = maya.dateparser.parse(block_dict['timestamp'])
        block_dict['timestamp'] = timestamp
    return block_dict


def extract_transactions_from_blocks(blocks):
    transactions = chain.from_iterable(
            map(extract_transactions_from_block, blocks))
    return transactions


def extract_transactions_from_block(_block):
    block = prepare_raw_block(_block)
    block_transactions = deepcopy(block['transactions'])
    for transaction_num, t in enumerate(block_transactions, 1):
        t = deepcopy(t)
        yield dict(block_num=block['block_num'],
                   timestamp=block['timestamp'],
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
        for op_num, _operation in enumerate(transaction['operations'], 1):
            operation = deepcopy(_operation)
            op_type, op = operation
            op.update(
                    block_num=transaction['block_num'],
                    transaction_num=transaction['transaction_num'],
                    operation_num=op_num,
                    timestamp=block['timestamp'],
                    type=op_type)
            yield op


def extract_operations_from_blocks(blocks):
    operations = chain.from_iterable(map(extract_operations_from_block, blocks))
    return operations
