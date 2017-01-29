# -*- coding: utf-8 -*-
from copy import deepcopy

from sqlalchemy import MetaData
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import UnicodeText
from sqlalchemy import Unicode

from sqlalchemy.schema import ForeignKeyConstraint

from sqlalchemy.types import TIMESTAMP

from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import object_session

from sqlalchemy.ext.declarative import declarative_base

import sbds.logging

from sbds.utils import block_info
from sbds.storages.db.utils import UniqueMixin


from sbds.storages.db import prepare_raw_block
from sbds.storages.db import extract_operations_from_block
from sbds.storages.db import extract_transactions_from_block

from sbds.storages.db.tables.enums import transaction_types_enum

from sbds.storages.db.tables.field_handlers import json_metadata
from sbds.storages.db.tables.field_handlers import amount
from sbds.storages.db.tables.field_handlers import amount_symbol
from sbds.storages.db.tables.field_handlers import comment_body

logger = sbds.logging.getLogger(__name__)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

Session = sessionmaker()



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

    __tablename__ = 'Blocks'
    __table_args__ = {
        'mysql_engine':'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }

    raw = Column(UnicodeText)
    block_num = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    previous = Column(Unicode(50))
    timestamp = Column(TIMESTAMP(timezone=False), index=True)
    witness = Column(Unicode(50))
    witness_signature = Column(Unicode(150))
    transaction_merkle_root = Column(Unicode(50))

    transactions = relationship('Transaction', back_populates='block')

    def __repr__(self):
        return "<Block(block_num='%s', timestamp='%s')>" % (
            self.block_num, self.timestamp)

    @classmethod
    def from_raw_block(cls, raw_block):
        prepared = cls._prepare_for_storage(raw_block)
        return cls(**prepared)

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
    def unique_hash(cls, *args, **kwargs):
        return kwargs['block_num']

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(cls.block_num == kwargs['block_num'])


class Transaction(Base, UniqueMixin):
    """
    Raw Format
    ==========
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
        }
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
    }

    Prepared Format
    ===============
    {
        "tx_id": 3893898,
        "block_num": 4000001,
        "transaction_num": 1,
        "ref_block_num": 2203,
        "ref_block_prefix": 3949810370,
        "expiration": "2016-08-11 22:00:18.000",
        "type": "comment"
    }
    """

    __tablename__ = 'Transactions'
    __table_args__ = (
        Index('ix_transactions', 'block_num', 'transaction_num', unique=True),
        {'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'}
    )

    tx_id = Column(Integer, primary_key=True, autoincrement=True)
    block_num = Column(ForeignKey(Block.block_num,
                                  use_alter=True,
                                  ondelete='CASCADE',
                                  onupdate='CASCADE'), nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    ref_block_num = Column(Integer, nullable=False)
    ref_block_prefix = Column(BigInteger, nullable=False)
    expiration = Column(TIMESTAMP(timezone=False), nullable=False)
    type = Column(transaction_types_enum, nullable=False, index=True)

    block = relationship('Block', back_populates='transactions')


    def __repr__(self):
        return "<Transaction(tx_id=%s, block_num='%s', transaction_num='%s' op_type='%s')>" % (
            self.tx_id, self.block_num, self.transaction_num, self.type)

    @classmethod
    def from_raw_block(cls, raw_block):
        transactions = cls._prepare_for_storage(raw_block=raw_block)
        return [cls(**tx) for tx in transactions]

    @classmethod
    def from_extracted_transaction(cls, _transaction, block_obj=None):
        transaction = cls._prepare_for_storage(extracted_transaction=_transaction,
                                               block_obj=block_obj)
        return cls(**transaction)

    @classmethod
    def _prepare_for_storage(cls, extracted_transaction=None, raw_block=None, block_obj=None):
        if extracted_transaction:
            return cls._prepare_from_extracted_transaction(extracted_transaction,
                                                           block_obj=block_obj)
        elif raw_block:
            return cls._prepare_from_raw_block(raw_block)

    @classmethod
    def _prepare_from_raw_block(cls, raw_block):
        transactions = extract_transactions_from_block(raw_block)
        prepared_transactions = map(cls._prepare_from_extracted_transaction, transactions)
        return list(prepared_transactions)

    @classmethod
    def _prepare_from_extracted_transaction(cls, extracted_transaction, block_obj=None):
        transaction = deepcopy(extracted_transaction)
        if 'operations' in transaction:
            del transaction['operations']
        if block_obj:
            transaction['block'] = block_obj
        return transaction

    @classmethod
    def get_or_create_from_raw_block(cls, raw_block, session=None):
        transactions = cls._prepare_from_raw_block(raw_block)
        return [cls.as_unique(session, **t) for t in transactions]


    def add_matching_tx_objs(self, tx_objs):
        txs = [tx for tx in tx_objs  if self.transaction_num==tx.transaction_num]
        for tx in txs:
            relation_name = tx.__tablename__
            setattr(self, relation_name, tx )

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return tuple([kwargs['block_num'], kwargs['transaction_num']])


    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(cls.block_num == kwargs['block_num'],
                            cls.transaction_num==kwargs['transaction_num'])



def from_raw_block(raw_block, session=None, new_block=True, new_transaction=True):
    from sbds.storages.db.tables.transaction_classes import TxBase
    block = Block.get_or_create_from_raw_block(raw_block, session=session)
    transactions = Transaction.get_or_create_from_raw_block(raw_block, session=session)
    block.transactions = transactions
    tx_transactions = TxBase.from_raw_block(raw_block, transactions=transactions, session=session)
    for tx in tx_transactions:
        tx.transaction = transactions[tx.transaction_num-1]
    return block


def create_all_from_block(raw_block, session=None):
    block_dict = prepare_raw_block(raw_block)
    info = block_info(block_dict)
    print(info['brief'].format(info))
    try:
        block = from_raw_block(raw_block, session=session)
        session.add(block)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        session.expunge_all()

def create_all_from_blocks(raw_blocks, session=None, new_block=False, new_transaction=False):
    for i, block in enumerate(raw_blocks, 1):
        try:
            create_all_from_block(block, session=session, new_block=new_block, new_transaction=new_transaction)
        except Exception as e:
            block_dict = prepare_raw_block(block)
            objs = from_raw_block(block)
            extra = dict(block_dict=block_dict, objs=objs, block_num=block_dict['block_num'], error=e, i=i)
            logger.error('create_all_from_blocks error', extra=extra)
            session.rollback()
            session.expunge_all()
