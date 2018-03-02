# -*- coding: utf-8 -*-
from functools import partial

import sqlalchemy.dialects

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import func

from toolz import dissoc

import sbds.sbds_json
from sbds.storages.db.tables import Base
from sbds.storages.db.tables.core import prepare_raw_block
from sbds.storages.db.utils import UniqueMixin


class Block(Base, UniqueMixin):
    """Steem Block class

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

    Args:

    Returns:

    """
    # pylint: enable=line-too-long
    __tablename__ = 'sbds_core_blocks'

    raw = Column(UnicodeText())
    block_num = Column(
        Integer, primary_key=True, autoincrement=False)
    block_id = Column(String(40), default='0000000000000000000000000000000000000000')
    previous = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=False), index=True)
    witness = Column(String(50), ForeignKey("sbds_meta_accounts.name")
                     )  # steem_type:{account_name_type}'
    witness_signature = Column(String(150))
    transaction_merkle_root = Column(String(40))

    def __repr__(self):
        return "<Block(block_num='%s', timestamp='%s')>" % (self.block_num,
                                                            self.timestamp)

    def dump(self):
        return dissoc(self.__dict__, '_sa_instance_state')

    def to_dict(self, include_raw=False):
        data = self.dump()
        if not include_raw:
            return dissoc(data, 'raw')

        return data

    def to_json(self):
        return sbds.sbds_json.dumps(self.to_dict())

    @classmethod
    def _prepare_for_storage(cls, raw_block):
        """
        Convert raw block to dict formatted for storage.

        Args:
            raw_block (Union[Dict[str, str], Dict[str, List]]):

        Returns:
            Union[Dict[str, str], Dict[str, int]]:
        """
        block = prepare_raw_block(raw_block)
        return dict(
            raw=block['raw'],
            block_num=block['block_num'],
            previous=block['previous'],
            timestamp=block['timestamp'],
            witness=block['witness'],
            witness_signature=block['witness_signature'],
            transaction_merkle_root=block['transaction_merkle_root'])

    @classmethod
    def get_or_create_from_raw_block(cls, raw_block, session=None):
        """
        Return Block instance from raw block, creating if necessary.

        Args:
            raw_block (Dict[str, str]):
            session (sqlalchemy.orm.session.Session):

        Returns:
            sbds.storages.db.tables.core.Block:
        """
        prepared = cls._prepare_for_storage(raw_block)
        return cls.as_unique(session, **prepared)

    @classmethod
    def from_raw_block(cls, raw_block):
        """
        Instantiate Block from raw block.

        Args:
            raw_block (Union[Dict[str, str], Dict[str, List]]):

        Returns:
            sbds.storages.db.tables.core.Block:
        """
        prepared = cls._prepare_for_storage(raw_block)
        return cls(**prepared)

    # pylint: disable=unused-argument
    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return kwargs['block_num']

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(cls.block_num == kwargs['block_num'])

    # pylint: enable=unused-argument

    @classmethod
    def highest_block(cls, session):
        """
        Return integer result of MAX(block_num) db query.

        This does not have the same meaning as last irreversible block, ie, it
        makes no claim that the all blocks lower than the MAX(block_num) exist
        in the database.

        Args:
            session (sqlalchemy.orm.session.Session):

        Returns:
            int:
        """
        highest = session.query(func.max(cls.block_num)).scalar()
        if not highest:
            return 0

        return highest

    @classmethod
    def count(cls, session, start=None, end=None):
        query = session.query(func.count(cls.timestamp)).with_hint(
            cls, 'USE INDEX(ix_sbds_core_blocks_timestamp)')
        if start is not None:
            query = query.filter(cls.block_num >= start)
        if end:
            query = query.filter(cls.block_num <= end)
        return query.scalar()

    @classmethod
    def count_missing(cls, session, last_chain_block):
        block_count = cls.count(session)
        return last_chain_block - block_count

    @classmethod
    def find_missing_range(cls, session, start, end):
        start = start or 1
        correct_range = range(start, end + 1)
        correct_block_count = (end + 1) - start
        actual_block_count = cls.count(session, start, end)
        if correct_block_count == actual_block_count:
            return []
        query = session.query(cls.block_num)
        query = query.filter(cls.block_num >= start, cls.block_num <= end)
        results = query.all()
        block_nums = (r.block_num for r in results)
        correct = set(correct_range)
        missing = correct.difference(block_nums)
        return missing

    @classmethod
    def get_missing_block_num_iterator(cls,
                                       session,
                                       last_chain_block,
                                       chunksize=100000):
        highest_block = cls.highest_block(session)
        # handle empty db case efficiently
        if highest_block == 0:
            num_chunks = (last_chain_block // chunksize) + 1
            chunks = []
            for i in range(1, num_chunks + 1):
                start = (i - 1) * chunksize
                if start == 0:
                    start = 1
                end = i * chunksize
                if end >= last_chain_block:
                    end = last_chain_block
                chunks.append(partial(range, start, end))
            return chunks

        num_chunks = (last_chain_block // chunksize) + 1
        chunks = []
        for i in range(1, num_chunks + 1):
            start = (i - 1) * chunksize
            end = i * chunksize
            if end >= last_chain_block:
                end = last_chain_block
            chunks.append(
                partial(cls.find_missing_range, session, start, end))
        return chunks

    @classmethod
    def find_missing(cls, session, last_chain_block, chunksize=1000000):
        missing_block_num_gen = cls.get_missing_block_num_iterator(
            session, last_chain_block, chunksize=chunksize)
        all_missing = []
        for missing_query in missing_block_num_gen:
            all_missing.extend(missing_query())
        return all_missing
