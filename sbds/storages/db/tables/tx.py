# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import SmallInteger
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.types import Enum
from toolz.dicttoolz import dissoc
from toolz.dicttoolz import get_in

import sbds.sbds_json
import sbds.sbds_logging
from .core import Base
from .core import extract_operations_from_block
from ..field_handlers import amount_field
from ..field_handlers import amount_symbol_field
from ..field_handlers import comment_body_field
from ..field_handlers import json_string_field
from ..query_helpers import standard_trailing_windows
from ..utils import UniqueMixin

logger = sbds.sbds_logging.getLogger(__name__)


class UndefinedTransactionType(Exception):
    """Exception raised when undefined transction is encountered"""


# noinspection PyMethodParameters
class TxBase(UniqueMixin):
    # pylint: disable=no-self-argument

    @declared_attr
    def __table_args__(cls):
        args = (PrimaryKeyConstraint('block_num', 'transaction_num',
                                     'operation_num'), {
                                         'mysql_engine': 'InnoDB',
                                         'mysql_charset': 'utf8mb4',
                                         'mysql_collate': 'utf8mb4_general_ci'
        })
        return getattr(cls, '__extra_table_args__', tuple()) + args

    # pylint: enable=no-self-argument

    block_num = Column(Integer, nullable=False, index=True)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime(timezone=False), index=True)

    _fields = dict()

    @classmethod
    def _prepare_for_storage(cls, **kwargs):
        try:
            data_dict = kwargs['data_dict']
            op_type = data_dict['type']
            tx_cls = cls.tx_class_for_type(op_type)
            _fields = tx_cls._fields.get(op_type)
            prepared = {k: v(data_dict) for k, v in _fields.items()}
            prepared['block_num'] = data_dict['block_num']
            prepared['transaction_num'] = data_dict['transaction_num']
            prepared['operation_num'] = data_dict['operation_num']
            prepared['timestamp'] = data_dict['timestamp']
            prepared['operation_type'] = op_type

            if 'class_tuple' in kwargs:
                return tx_cls, prepared
            else:
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
            logger.error(e, extra=extra)
            return None

    @classmethod
    def from_raw_block(cls, raw_block):
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
                tx_cls = cls.tx_class_for_type(op_type)
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

    @classmethod
    def tx_class_for_type(cls, tx_type):
        try:
            return tx_class_map[tx_type]
        except KeyError:
            raise UndefinedTransactionType(tx_type)

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

    @classmethod
    def from_to_filter(cls, query, _from=None, to=None):
        if isinstance(_from, int):
            query = cls.block_num_window_filter(query, _from=_from)
        elif isinstance(_from, datetime):
            query = cls.datetime_window_filter(query, _from=_from)

        if isinstance(to, int):
            query = cls.block_num_window_filter(query, to=to)
        elif isinstance(to, datetime):
            query = cls.datetime_window_filter(query, to=to)

        return query

    @classmethod
    def block_num_window_filter(cls, query, _from=None, to=None):
        if _from:
            query = query.filter(cls.block_num >= _from)
        if to:
            query = query.filter(cls.block_num <= to)
        return query

    @classmethod
    def datetime_window_filter(cls, query, _from=None, to=None):
        if _from:
            query = query.filter(cls.timestamp >= _from)
        if to:
            query = query.filter(cls.timestamp <= to)
        return query

    @classmethod
    def standard_trailing_windowed_queries(cls, query):
        """

        Args:
            query (sqlalchemy.orm.query.Query):

        Yields:
            sqlalchemy.orm.query.Query
        """
        for window in standard_trailing_windows():
            yield cls.datetime_window_filter(query, **window)

    @classmethod
    def standard_windowed_count(cls, session):
        count_query = cls.count_query(session)
        for window_query in cls.standard_trailing_windowed_queries(
                count_query):
            yield window_query.scalar()

    @classmethod
    def _count_index_name(cls):
        # pylint: disable=no-member
        return 'ix_%s_timestamp' % cls.__tablename__

    @classmethod
    def count_query(cls, session):
        ix = cls._count_index_name()
        ix_stmt = 'USE INDEX(%s)' % ix
        return session.query(func.count(cls.timestamp)).with_hint(cls, ix_stmt)

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


# pylint: disable=line-too-long, bad-continuation, too-many-lines, no-self-argument
class TxAccountCreate(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 3620775392,
        "expiration": "2016-03-30T07:05:03",
        "operations": [
            [
                "account_create",
                {
                    "owner": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM8MN3FNBa8WbEpxz3wGL3L1mkt6sGnncH8iuto7r8Wa3T9NSSGT",
                                1
                            ]
                        ]
                    },
                    "memo_key": "STM6Gkj27XMkoGsr4zwEvkjNhh4dykbXmPFzHhT8g86jWsqu3U38X",
                    "active": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM8HCf7QLUexogEviN8x1SpKRhFwg2sc8LrWuJqv7QsmWrua6ZyR",
                                1
                            ]
                        ]
                    },
                    "new_account_name": "fabian",
                    "posting": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM8EhGWcEuQ2pqCKkGHnbmcTNpWYZDjGTT7ketVBp4gUStDr2brz",
                                1
                            ]
                        ]
                    },
                    "creator": "hello",
                    "json_metadata": "{}",
                    "fee": "0.000 STEEM"
                }
            ]
        ],
        "signatures": [
            "2051b9c61cdd9df1f04e5d37529a72c9d4419c1e0b466d78c156c383aa951b21eb3f13b5bcbe9d0caf883143a15ff911c2d2cac9c466a7f619618bb3b4d24612b5"
        ],
        "ref_block_num": 29707,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "tx_id": 7973,
        "fee": 0.0000,
        "creator": "hello",
        "new_account_name": "fabian",
        "owner_key": "STM8MN3FNBa8WbEpxz3wGL3L1mkt6sGnncH8iuto7r8Wa3T9NSSGT",
        "active_key": "STM8HCf7QLUexogEviN8x1SpKRhFwg2sc8LrWuJqv7QsmWrua6ZyR",
        "posting_key": "STM8EhGWcEuQ2pqCKkGHnbmcTNpWYZDjGTT7ketVBp4gUStDr2brz",
        "memo_key": "STM6Gkj27XMkoGsr4zwEvkjNhh4dykbXmPFzHhT8g86jWsqu3U38X",
        "json_metadata": "{}"
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_account_creates'

    fee = Column(Numeric(15, 6), nullable=False)
    creator = Column(Unicode(50), nullable=False, index=True)
    new_account_name = Column(Unicode(50))
    owner_key = Column(Unicode(80), nullable=False)
    active_key = Column(Unicode(80), nullable=False)
    posting_key = Column(Unicode(80), nullable=False)
    memo_key = Column(Unicode(250), nullable=False)
    json_metadata = Column(UnicodeText)

    _fields = dict(account_create=dict(
        creator=lambda x: x.get('creator'),
        fee=lambda x: amount_field(x.get('fee'), num_func=float),
        new_account_name=lambda x: x.get('new_account_name'),
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'),
        owner_key=lambda x: get_in(['owner', 'key_auths', 0, 0], x),
        active_key=lambda x: get_in(['active', 'key_auths', 0, 0], x),
        posting_key=lambda x: get_in(['posting', 'key_auths', 0, 0], x)))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxAccountCreateWithDelegation(Base, TxBase):
    """


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_account_create_with_delegations'

    fee = Column(Numeric(15, 6), nullable=False)
    delegation = Column(Numeric(15, 6), nullable=False)
    creator = Column(Unicode(50), nullable=False, index=True)
    new_account_name = Column(Unicode(50), index=True)
    owner_key = Column(Unicode(80), nullable=False)
    active_key = Column(Unicode(80), nullable=False)
    posting_key = Column(Unicode(80), nullable=False)
    memo_key = Column(Unicode(250), nullable=False)
    json_metadata = Column(UnicodeText)

    _fields = dict(account_create_with_delegation=dict(
        fee=lambda x: amount_field(x.get('fee'), num_func=float),
        delegation=lambda x: amount_field(x.get('delegation'), num_func=float),
        creator=lambda x: x.get('creator'),
        new_account_name=lambda x: x.get('new_account_name'),
        owner_key=lambda x: get_in(['owner', 'key_auths', 0, 0], x),
        active_key=lambda x: get_in(['active', 'key_auths', 0, 0], x),
        posting_key=lambda x: get_in(['posting', 'key_auths', 0, 0], x),
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxRequestAccountRecovery(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 392888852,
        "expiration": "2016-07-18T00:14:45",
        "operations": [
            [
                "request_account_recovery",
                {
                    "account_to_recover": "gandalf",
                    "new_owner_authority": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM6LYxj96zdypHYqgDdD6Nyh2NxerN3P1Mp3ddNm7gci63nfrSuZ",
                                1
                            ]
                        ]
                    },
                    "recovery_account": "steem",
                    "extensions": []
                }
            ]
        ],
        "signatures": [
            "1f6b0f44985aa8f476385078b69366b0868b45b666f717b34e074b98ca97a767b6209a931e998912f51b2f7d490a6283c3ce9c3d1f2a42a4695bda1e7a6786d0d3"
        ],
        "ref_block_num": 11112,
    "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_request_account_recoveries'

    recovery_account = Column(Unicode(50))
    account_to_recover = Column(Unicode(50), nullable=False)
    recovered = Column(Boolean, default=False)

    _fields = dict(request_account_recovery=dict(
        # FIXME
        operation_num=lambda x: x.get('operation_num'),
        recovery_account=lambda x: x.get('recovery_account'),
        account_to_recover=lambda x: x.get('account_to_recover'),
        recovered=lambda x: False))

    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxRecoverAccount(Base, TxBase):
    """
    {
        "operations": [
            [
                "recover_account",
                {
                    "recent_owner_authority": {
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM6Wf68LVi22QC9eS8LBWykRiSrKKp5RTWXcNqjh3VPNhiT9xFxx",
                                1
                            ]
                        ],
                        "weight_threshold": 1
                    },
                    "new_owner_authority": {
                        "account_auths": [],
                        "key_auths": [
                            [
                                "STM82miH8qam2G2WPPjgyquPBrUbenGDHjhZMxqaKqCugWhcuqZzW",
                                1
                            ]
                        ],
                        "weight_threshold": 1
                    },
                    "extensions": [],
                    "account_to_recover": "steemychicken1"
                }
            ]
        ],
        "expiration": "2016-07-18T05:46:33",
        "signatures": [
            "202c2c3902d513bb7f22e833576ea8418fdf7be3a08b0736d1de03c3289c5db11e1a95af820703e1407b8f3c0b030d857f666132b10be165b7569faba0442790f5",
            "2059587d734535c43caf33a706404d813897e8887ad1696750435be63dfae26fde5995a2c6c8cf295c380d89152abe97f4990f9c78a0e9095a96e6e2432dd88e05"
        ],
        "ref_block_num": 17711,
        "ref_block_prefix": 311057647,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_recover_accounts'

    recovery_account = Column(Unicode(50))
    account_to_recover = Column(Unicode(50), nullable=False)
    recovered = Column(Boolean, default=False)

    _fields = dict(recover_account=dict(
        recovery_account=lambda x: x.get('recovery_account'),
        account_to_recover=lambda x: x.get('account_to_recover'),
        recovered=lambda x: True))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxAccountUpdate(Base, TxBase):
    """Raw Format
    {
        "memo_key": "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
        "active": {
            "account_auths": [],
            "weight_threshold": 1,
            "key_auths": [
                [
                    "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
                    1
                ],
                [
                    "STM76EQNV2RTA6yF9TnBvGSV71mW7eW36MM7XQp24JxdoArTfKA76",
                    1
                ]
            ]
        },
        "account": "theoretical",
        "json_metadata": ""
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_account_updates'

    account = Column(Unicode(50))
    key_auth1 = Column(Unicode(80))
    key_auth2 = Column(Unicode(80))
    memo_key = Column(Unicode(250))
    json_metadata = Column(UnicodeText)

    _fields = dict(account_update=dict(
        account=lambda x: x.get('account'),
        key_auth1=lambda x: None,  # TODO fix null
        key_auth2=lambda x: None,  # TODO fix null
        memo_key=lambda x: x.get('memo_key'),
        json_metadata=lambda x: x.get('json_metadata'), ))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxChangeRecoveryAccount(Base, TxBase):
    """Raw Format
    ==========

    {
        "account_to_recover": "barrie",
        "extensions": [],
        "new_recovery_account": "boombastic"
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_change_recovery_accounts'

    account_to_recover = Column(Unicode(50))
    new_recovery_account = Column(Unicode(50))

    _fields = dict(change_recovery_account=dict(
        account_to_recover=lambda x: x.get('account_to_recover'),
        new_recovery_account=lambda x: x.get('new_recovery_account')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxAccountWitnessProxy(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 2749880717,
        "operations": [
            [
                "account_witness_proxy",
                {
                    "proxy": "abit",
                    "account": "puppies"
                }
            ]
        ],
        "signatures": [
            "2066825bf5033b1a85b3f26c43bc853aa2e1e57ecdd400f61ea0ed444906836c323345c6b04cdbbb39637ed180ddf7a8eacc9d36086158140d1dec5788b73a01b4"
        ],
        "ref_block_num": 31712,
        "expiration": "2016-04-08T15:47:00",
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 22,
        "tx_id": 44236,
        "account": "puppies",
        "Proxy": "abit"
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_account_witness_proxies'

    account = Column(Unicode(50), nullable=False)
    Proxy = Column(Unicode(50), nullable=False)

    _fields = dict(account_witness_proxy=dict(
        account=lambda x: x.get('account'),
        Proxy=lambda x: x.get('proxy'),  # TODO fix capitalization
    ))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxAccountWitnessVote(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 575883867,
        "operations": [
            [
                "account_witness_vote",
                {
                    "witness": "berniesanders",
                    "account": "donalddrumpf",
                    "approve": true
                }
            ]
        ],
        "signatures": [
            "1f7782f6c379d14c97718489b5ebca68fa25b3042e781d2f620ccc4927fbf4d3f30e60ba424cd906eb75b87cd4002bf982bc2ba9dc0f2c7b136b566de7416a170b"
        ],
        "ref_block_num": 57831,
        "expiration": "2016-03-28T23:43:36",
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "tx_id": 6055,
        "witness": "berniesanders",
        "id": 1,
        "account": "donalddrumpf",
        "approve": True
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_account_witness_votes'

    account = Column(Unicode(50), nullable=False)
    witness = Column(Unicode(50), nullable=False)
    approve = Column(Boolean, default=False)

    _fields = dict(account_witness_vote=dict(
        account=lambda x: x.get('account'),
        approve=lambda x: x.get('appove'),
        witness=lambda x: x.get('witness')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxClaimRewardBalance(Base, TxBase):
    """


    Args:

    Returns:

    {
      "ref_block_num": 18849,
      "ref_block_prefix": 3618600471,
      "expiration": "2017-03-30T20:15:54",
      "operations": [
        [
          "claim_reward_balance",
          {
            "account": "ocrdu",
            "reward_steem": "0.017 STEEM",
            "reward_sbd": "0.011 SBD",
            "reward_vests": "185.025103 VESTS"
          }
        ]
      ],
      "extensions": [],
      "signatures": [
        "2074300e7bc9064b7aa47fe14be844d53737e0981daa7c2b5a3a1c3ffe884ea1866d62bc5d16230495536492ab62493c483f484d67422d25a7d18078d10ca740fb"
      ]
    }


    """

    __tablename__ = 'sbds_tx_claim_reward_balances'

    account = Column(Unicode(50), index=True, nullable=False)
    reward_steem = Column(Numeric(15, 6))
    reward_sbd = Column(Numeric(15, 6))
    reward_vests = Column(Numeric(15, 6))

    _fields = dict(claim_reward_balance=dict(
        account=lambda x: x.get('account'),
        reward_steem=lambda x: amount_field(x.get('reward_steem'), num_func=float),
        reward_sbd=lambda x: amount_field(x.get('reward_sbd'), num_func=float),
        reward_vests=lambda x: amount_field(x.get('reward_vests'), num_func=float), ))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxComment(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 3071757153,
        "operations": [
            [
                "comment",
                {
                    "author": "xeldal",
                    "body": "This is xeldal, an experienced witness. Will you vote for me?",
                    "json_metadata": "{}",
                    "title": "xeldal Witness Thread",
                    "permlink": "xeldal-witness-post",
                    "parent_author": "",
                    "parent_permlink": "witness-category"
                }
            ]
        ],
        "signatures": [
            "1f332f851112774103c4a12a97941f1c39a1c30a0561e64fbbe756d0860f7e68a206f2f57dfd15b77ecf3ce13fcffd6e66ae4b65a8df29bc01682876e34eb3cecf"
        ],
        "ref_block_num": 32379,
        "expiration": "2016-04-08T16:20:27",
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "tx_id": 44351,
        "author": "xeldal",
        "body": "This is xeldal, an experienced witness. Will you vote for me?",
        "parent_permlink": "witness-category",
        "title": "xeldal Witness Thread",
        "permlink": "xeldal-witness-post",
        "id": 25,
        "parent_author": "",
        "json_metadata": "{}"
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_comments'

    author = Column(Unicode(50), nullable=False, index=True)
    permlink = Column(Unicode(512), nullable=False, index=True)
    parent_author = Column(Unicode(50), index=True)
    parent_permlink = Column(Unicode(512))
    title = Column(Unicode(512))
    body = Column(UnicodeText)
    json_metadata = Column(UnicodeText)

    _fields = dict(comment=dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        parent_author=lambda x: x.get('parent_author'),
        parent_permlink=lambda x: x.get('parent_permlink'),
        title=lambda x: x.get('title'),
        body=lambda x: comment_body_field(x['body']),
        json_metadata=lambda x: x.get('json_metadata')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)

    @classmethod
    def find_parent_from_prepared(cls, session, prepared):
        return session.query(cls).filter(
            cls.parent_permlink == prepared['parent_permlink'],
            cls.parent_author == prepared['parent_author']).one_or_none()

    @classmethod
    def post_filter(cls, query):
        return query.filter(cls.parent_author == '')

    @classmethod
    def comment_filter(cls, query):
        return query.filter(cls.parent_author != '')

    @classmethod
    def count_query(cls, session):
        return session.query(func.count(cls.block_num))

    @classmethod
    def post_count_query(cls, session):
        count_query = cls.count_query(session)
        return cls.post_filter(count_query)

    @classmethod
    def comment_count_query(cls, session):
        count_query = cls.count_query(session)
        return cls.comment_filter(count_query)

    @property
    def type(self):
        # include self.author to assure decision isn't made on a blank instance
        if all([self.author, self.parent_author]):
            return 'comment'
        elif self.author and not self.parent_author:
            return 'post'

    @property
    def is_post(self):
        return self.type == 'post'

    @property
    def is_comment(self):
        return self.type == 'comment'


class TxCommentOption(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 3739556666,
        "expiration": "2016-08-12T07:02:19",
        "operations": [
            [
                "comment_options",
                {
                    "author": "testing001",
                    "allow_curation_rewards": true,
                    "max_accepted_payout": "1000.000 SBD",
                    "percent_steem_dollars": 5000,
                    "allow_votes": true,
                    "permlink": "testing6",
                    "extensions": []
                }
            ]
        ],
        "signatures": [
            "1f47ff6711fad1ab07a9e10ce91e1fd84ca49629a6f45af6aca67150705e651b2006b5548520995bedd09daf6f597d2bc68a30c7c161b4600e14f0032e69235fcf"
        ],
        "ref_block_num": 13118,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 1,
        "tx_id": 3924992,
        "author": "testing001",
        "permlink": "testing6",
        "max_accepted_payout": 1000.0000,
        "percent_steem_dollars": 5000,
        "allow_votes": True,
        "allow_curation_rewards": True
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_comments_options'

    author = Column(Unicode(50), nullable=False)
    permlink = Column(Unicode(512), nullable=False)
    max_accepted_payout = Column(Numeric(15, 6), nullable=False)
    percent_steem_dollars = Column(SmallInteger, default=0)
    allow_votes = Column(Boolean, nullable=False)
    allow_curation_rewards = Column(Boolean, nullable=False)

    _fields = dict(comment_options=dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        max_accepted_payout=lambda x: amount_field(x.get('max_accepted_payout'), num_func=float),
        percent_steem_dollars=lambda x: x.get('percent_steem_dollars'),
        allow_votes=lambda x: x.get('allow_votes'),
        allow_curation_rewards=lambda x: x.get('allow_curation_rewards')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxConvert(Base, TxBase):
    """Raw Format
    ==========
    {
        'expiration': '2016-07-04T00:29:39',
        'extensions': [],
        'operations': [['convert',{
            'amount': '5.000 SBD',
            'owner': 'summon',
            'requestid': 1467592156
            }]],
        'ref_block_num': 5864,
        'ref_block_prefix': 521569582,
        'signatures': ['1f0cd39195d45d5d40cd92651081670b5a799217d615c311921fc1981a0898703d1864555148c2e1246a19fa8ea1b80b4dd4474df86fc9a9c9d6a9c8576d467687']
    }

    Prepared Format
    ===============
    {
        "owner": "summon",
        "amount": "5.000 SBD",
        "requestid": 1467592156
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_converts'

    owner = Column(Unicode(50), nullable=False)
    requestid = Column(BigInteger, nullable=False)
    amount = Column(Numeric(15, 6), nullable=False)

    _fields = dict(convert=dict(
        owner=lambda x: x.get('owner'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        requestid=lambda x: x.get('requestid')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxCustom(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 449600556,
        "ref_block_num": 54561,
        "operations": [
            [
                "custom",
                {
                    "id": 777,
                    "data": "066e6f69737932056c656e6b61032e0640ec51dbcfb761bd927a732e134deff42dbed04bc42300f27f3048b8b44802be956c36eef2e0d3594b794b428a21b48fe41874d41cf12feb8e421e11b3702f24e94b559f4505006dbafb90208bf88f7bb550f6db0713cbb4be6c214c50c16aa62413383f26f9efbb4fe5bf3f",
                    "required_auths": [
                        "noisy2"
                    ]
                }
            ]
        ],
        "expiration": "2017-01-09T01:32:36",
        "signatures": [
            "1f38daabe10814c20f78bba5cbeed5f9115eb9d420278540bddf9e3c6e84fe3ca33da6b32127faf0d30cc0d618711edd294b95fa92787398cb7f0dfb7280509db3"
        ],
        "extensions": []
    }
    """

    __tablename__ = 'sbds_tx_customs'

    tid = Column(Unicode(50), nullable=False)
    required_auths = Column(Unicode(250))
    data = Column(UnicodeText)

    common = dict(
        tid=lambda x: x.get('id'),
        data=lambda x: x.get('data'),
        required_auths=lambda x: x.get('required_auths'), )
    _fields = dict(custom=common)
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)

    def to_dict(self, decode_json=True):
        data_dict = self.dump()
        if isinstance(data_dict.get('required_auths'), str) and decode_json:
            data_dict['required_auths'] = sbds.sbds_json.loads(
                data_dict['required_auths'])
        return data_dict


class TxCustomJSON(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 1629956753,
        "ref_block_num": 10739,
        "operations": [
            [
                "custom_json",
                {
                    "id": "follow",
                    "json": "[\"follow\",{\"follower\":\"joanaltres\",\"following\":\"str8jackitjake\",\"what\":[\"blog\"]}]",
                    "required_posting_auths": [
                        "joanaltres"
                    ],
                    "required_auths": []
                }
            ]
        ],
        "expiration": "2017-02-26T15:54:57",
        "signatures": [
            "200d43fadd4a11d02d2dca36d0092b4439b674db406c024d9ef0eef08041a9500b45e5807a69d9e8ed9457ee675ba76ccdaee1587bef9902a680da7fd7f498e620"
        ],
        "extensions": []
    }
    """

    __tablename__ = 'sbds_tx_custom_jsons'

    tid = Column(Unicode(50), nullable=False, index=True)
    required_auths = Column(Unicode(250))
    required_posting_auths = Column(Unicode(250))
    json = Column(UnicodeText)

    common = dict(
        tid=lambda x: x.get('id'),
        json=lambda x: x.get('json'),
        required_auths=lambda x: json_string_field(x.get('required_auths')),
        required_posting_auths=lambda x: json_string_field(x.get('required_posting_auths')), )
    _fields = dict(custom_json=common)
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)

    def to_dict(self, decode_json=True):
        data_dict = self.dump()
        if isinstance(data_dict.get('required_auths'), str) and decode_json:
            data_dict['required_auths'] = sbds.sbds_json.loads(
                data_dict['required_auths'])
        if isinstance(data_dict.get('required_posting_auths'),
                      str) and decode_json:
            data_dict['required_posting_auths'] = sbds.sbds_json.loads(
                data_dict['required_posting_auths'])
        if isinstance(data_dict.get('json'), str) and decode_json:
            data_dict['json'] = sbds.sbds_json.loads(data_dict['json'])
        return data_dict


class TxDelegateVestingShares(Base, TxBase):
    """
    {
      "ref_block_num": 13361,
      "ref_block_prefix": 1969744882,
      "expiration": "2017-03-30T15:39:45",
      "operations": [
        [
          "delegate_vesting_shares",
          {
            "delegator": "liberosist",
            "delegatee": "dunia",
            "vesting_shares": "94599167.138276 VESTS"
          }
        ]
      ],
      "extensions": [],
      "signatures": [
        "2058ca7ba73a5787be2b5cf62595251279de63344709240f6300a8625f0f26cc550fa5b3ce740220b085c7b539f6b822047d4136cafc8245f60bcca5822d929f8a"
      ]
    }
    """

    __tablename__ = 'sbds_tx_delegate_vesting_shares'

    delegator = Column(Unicode(50), index=True)
    delegatee = Column(Unicode(50), index=True)
    vesting_shares = Column(Numeric(15, 6))

    _fields = dict(delegate_vesting_shares=dict(
        delegator=lambda x: x.get('delegator'),
        delegatee=lambda x: x.get('delegatee'),
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float), ))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxDeclineVotingRights(Base, TxBase):

    __tablename__ = 'sbds_tx_decline_voting_rights'

    account = Column(Unicode(50), nullable=False)
    decline = Column(Boolean, default=True)

    _fields = dict(decline_voting_rights=dict(
        account=lambda x: x.get('account'),
        decline=lambda x: x.get('decline')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxDeleteComment(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 3023139187,
        "expiration": "2016-06-06T19:34:27",
        "operations": [
            [
                "delete_comment",
                {
                    "author": "jsc",
                    "permlink": "tests-delete"
                }
            ]
        ],
        "signatures": [
            "2044602e8a51a6f44827be54fb5fec8b53698fdf608a5fdd5943af71f288229fc078104b9798391989e15153f5f1aeb370d74ec027fefe4b5372a6c90d35b175f3"
        ],
        "ref_block_num": 12211,
        "extensions": []
    }


    Prepared Format
    ===============
    {
        "id": 1,
        "tx_id": 309111,
        "author": "jsc",
        "permlink": "tests-delete"
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_delete_comments'

    author = Column(Unicode(50), nullable=False)
    permlink = Column(Unicode(250), nullable=False)

    _fields = dict(delete_comment=dict(
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxEscrowApprove(Base, TxBase):
    """
    Raw Format
    ==========
    {
        "from": "xtar",
        "agent": "on0tole",
        "to": "testz",
        "escrow_id": 59102208,
        "approve": true,
        "who": "on0tole"
    }
    """

    __tablename__ = 'sbds_tx_escrow_approves'

    _from = Column('from', Unicode(50), index=True)
    agent = Column(Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    who = Column(Unicode(50), index=True)
    escrow_id = Column(Integer)
    approve = Column(Boolean)

    _fields = dict(escrow_approve=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        escrow_id=lambda x: x.get('request_id'),
        who=lambda x: x.get('who'),
        approve=lambda x: x.get('approve'), ))

    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxEscrowDispute(Base, TxBase):
    """
    Raw Format
    ==========
    {
        "escrow_id": 72526562,
        "from": "anonymtest",
        "agent": "xtar",
        "who": "anonymtest",
        "to": "someguy123"
    }
    """

    __tablename__ = 'sbds_tx_escrow_disputes'

    _from = Column('from', Unicode(50), index=True)
    agent = Column(Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    who = Column(Unicode(50), index=True)
    escrow_id = Column(Integer)
    approve = Column(Boolean)

    _fields = dict(escrow_dispute=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        escrow_id=lambda x: x.get('request_id'),
        who=lambda x: x.get('who'), ))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxEscrowRelease(Base, TxBase):
    """
    Raw Format
    ==========
    {
        "from": "anonymtest",
        "agent": "xtar",
        "to": "someguy123",
        "escrow_id": 72526562,
        "steem_amount": "0.000 STEEM",
        "sbd_amount": "5.000 SBD",
        "who": "xtar",
        "receiver": "someguy123"
    }
    """

    __tablename__ = 'sbds_tx_escrow_releases'

    _from = Column('from', Unicode(50), index=True)
    agent = Column(Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    escrow_id = Column(Integer)
    steem_amount = Column(Numeric(15, 6))
    sbd_amount = Column(Numeric(15, 6))
    who = Column(Unicode(50), index=True)
    receiver = Column(Unicode(50), index=True)

    _fields = dict(escrow_release=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        who=lambda x: x.get('who'),
        receiver=lambda x: x.get('receiver'),
        escrow_id=lambda x: x.get('request_id'),
        sbd_amount=lambda x: amount_field(x.get('sbd_amount'), num_func=float),
        steem_amount=lambda x: amount_field(x.get('steem_amount'), num_func=float)))

    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxEscrowTransfer(Base, TxBase):
    """
    Raw Format
    ==========
    {
     "from": "siol",
     "agent": "fabien",
     "escrow_expiration": "2017-02-28T11:22:39",
     "to": "james",
     "ratification_deadline": "2017-02-26T11:22:39",
     "escrow_id": 23456789,
     "steem_amount": "0.000 STEEM",
     "json_meta": "{}",
     "sbd_amount": "1.000 SBD",
     "fee": "0.100 SBD"
    }
    """

    __tablename__ = 'sbds_tx_escrow_transfers'

    _from = Column('from', Unicode(50), index=True)
    agent = Column(Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    escrow_id = Column(Integer)
    steem_amount = Column(Numeric(15, 6))
    sbd_amount = Column(Numeric(15, 6))

    json_metadata = Column(UnicodeText)
    fee_amount = Column(Numeric(15, 6))
    fee_amount_symbol = Column(Unicode(5))
    escrow_expiration = Column(DateTime(timezone=False), index=True)
    ratification_deadline = Column(DateTime(timezone=False), index=True)

    _fields = dict(escrow_transfer=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        agent=lambda x: x.get('agent'),
        escrow_id=lambda x: x.get('request_id'),
        sbd_amount=lambda x: amount_field(x.get('sbd_amount'), num_func=float),
        steem_amount=lambda x: amount_field(x.get('steem_amount'), num_func=float),
        fee_amount=lambda x: amount_field(x.get('fee'), num_func=float),
        fee_amount_symbol=lambda x: amount_symbol_field(x.get('fee')),
        json_metadata=lambda x: x.get('json_metadata'),
        escrow_expiration=lambda x: x.get('escrow_expiration'),
        ratification_deadline=lambda x: x.get('ratification_deadline')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxFeedPublish(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 336265640,
        "expiration": "2016-04-26T23:08:06",
        "operations": [
            [
                "feed_publish",
                {
                    "exchange_rate": {
                        "quote": "1.000 STEEM",
                        "base": "0.374 SBD"
                    },
                    "publisher": "smooth.witness"
                }
            ]
        ],
        "signatures": [
            "1f45f20c78e105eba93946b4366293f28a1d5b5e6e52e2007e8c0965c19bdd5b1464ba7a6b274d1a483715e3a883125106905c24e57092bc89247689cdc335c3fc"
        ],
        "ref_block_num": 19946,
        "extensions": []
    }


    Prepared Format
    ===============
    {
        "id": 23,
        "tx_id": 157612,
        "publisher": "smooth.witness",
        "exchange_rate_base": 0.3740,
        "exchange_rate_quote": 1.0000
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_feed_publishes'

    publisher = Column(Unicode(50), nullable=False)
    exchange_rate_base = Column(Numeric(15, 6), nullable=False)
    exchange_rate_quote = Column(Numeric(15, 6), nullable=False)

    _fields = dict(feed_publish=dict(
        publisher=lambda x: x.get('publisher'),
        exchange_rate_base=lambda x: amount_field(
            get_in(['exchange_rate', 'base'], x), num_func=float),
        exchange_rate_quote=lambda x: amount_field(
            get_in(['exchange_rate', 'quote'], x), num_func=float)
    )
    )
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxLimitOrderCancel(Base, TxBase):
    """

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_limit_order_cancels'

    owner = Column(Unicode(50), nullable=False)
    orderid = Column(BigInteger, nullable=False)

    _fields = dict(limit_order_cancel=dict(
        owner=lambda x: x.get('owner'), orderid=lambda x: x.get('orderid')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxLimitOrderCreate(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 843461126,
        "expiration": "2016-07-01T13:33:03",
        "operations": [
            [
                "limit_order_create",
                {
                    "owner": "adm",
                    "amount_to_sell": "5.000 STEEM",
                    "min_to_receive": "1.542 SBD",
                    "orderid": 9,
                    "fill_or_kill": false,
                    "expiration": "2016-07-01T13:34:03"
                }
            ]
        ],
        "signatures": [
            "1f28e4e49e31cb9f22176fe142b3334d2459ec75cd70e48b2f536f6dc38deb8e8e5402e2cb878e0bc8cee2dc1280c480acdabe5807de5f7bc5c59ccf788920cdeb"
        ],
        "ref_block_num": 969,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_limit_order_creates'

    owner = Column(Unicode(50), nullable=False)
    orderid = Column(BigInteger, nullable=False)
    cancel = Column(Boolean, default=False)
    amount_to_sell = Column(Numeric(15, 6))
    # sell_symbol = Column(Unicode(5))
    min_to_receive = Column(Numeric(15, 6))
    # receive_symbol = Column(Unicode(5))
    fill_or_kill = Column(Boolean, default=False)
    expiration = Column(DateTime)

    _fields = dict(limit_order_create=dict(
        owner=lambda x: x.get('owner'),
        orderid=lambda x: x.get('orderid'),
        cancel=lambda x: x.get('cancel'),
        amount_to_sell=lambda x: amount_field(x.get('amount_to_sell'), num_func=float),
        # sell_symbol=lambda x: x['amount_to_sell'].split()[1],
        min_to_receive=lambda x: amount_field(x.get('min_to_receive'), num_func=float),
        # receive_symbol=lambda x: x['min_to_receive'].split()[1],
        fill_or_kill=lambda x: x.get('fill_or_kill'),
        expiration=lambda x: x.get('expiration')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxPow2(Base, TxBase):
    """Raw Format
    ==========

    {
        "ref_block_prefix": 2030100032,
        "expiration": "2017-01-20T17:43:24",
        "operations": [
            [
                "pow2",
                {
                    "work": [
                        1,
                        {
                            "prev_block": "0083f04940de00790a548572b5f7a09d2a9e6676",
                            "pow_summary": 3542335882,
                            "proof": {
                                "inputs": [
                                    2930666,
                                    3055534,
                                    16227194,
                                    1878724,
                                    3055534,
                                    3370375,
                                    10368718,
                                    8279292,
                                    1878724,
                                    12665269,
                                    13416647,
                                    14101780,
                                    14954112,
                                    16332900,
                                    7269530,
                                    13055417,
                                    16709657,
                                    14859041,
                                    8879475,
                                    3839300,
                                    8879475,
                                    14954112,
                                    3370375,
                                    7416112,
                                    15613499,
                                    15613499,
                                    6086878,
                                    9856240,
                                    587509,
                                    587509,
                                    6047993,
                                    10368718,
                                    6449363,
                                    7416112,
                                    15056305,
                                    8279292,
                                    13055417,
                                    6086878,
                                    16332900,
                                    14859041,
                                    308997,
                                    13416647,
                                    14101780,
                                    2930666,
                                    2552223,
                                    12665269,
                                    2552223,
                                    6047993,
                                    308997,
                                    16709657,
                                    3654688,
                                    9885009,
                                    15056305,
                                    9856240,
                                    7269530,
                                    3654688,
                                    5757028,
                                    16227194,
                                    5757028,
                                    3839300,
                                    9885009,
                                    6449363,
                                    2141293,
                                    2141293
                                ],
                                "n": 140,
                                "seed": "3dbe4a5694af55d7bccc622a7b2d41293c26d5290ca43bd9754104d99c52dd2a",
                                "k": 6
                            },
                            "input": {
                                "prev_block": "0083f04940de00790a548572b5f7a09d2a9e6676",
                                "nonce": "11247522470727134118",
                                "worker_account": "nori"
                            }
                        }
                    ],
                    "props": {
                        "account_creation_fee": "0.001 STEEM",
                        "sbd_interest_rate": 1000,
                        "maximum_block_size": 131072
                    }
                }
            ]
        ],
        "signatures": [
            "1f0e5ef13b709989d1256def83f45dd8a89b821cefdf3f5feefa380508233afb0d2c457d04e2c64937f36ff4d6a86e26303f710db1d92749ac6fc8fa8f95259e95"
        ],
        "ref_block_num": 61513,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_pow2s'

    worker_account = Column(Unicode(50), nullable=False, index=True)
    block_id = Column(Unicode(40), nullable=False)

    _fields = dict(pow2=dict(
        worker_account=lambda x: get_in(['work', 1, 'input', 'worker_account'], x),
        block_id=lambda x: get_in(['work', 1, 'input', 'prev_block'], x)))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxPow(Base, TxBase):
    """Raw Format
    ==========

    op_type=='pow'
    ==============
    {
        "ref_block_prefix": 2181793527,
        "expiration": "2016-03-24T18:00:21",
        "operations": [
            [
                "pow",
                {
                    "props": {
                        "account_creation_fee": "100.000 STEEM",
                        "sbd_interest_rate": 1000,
                        "maximum_block_size": 131072
                    },
                    "work": {
                        "signature": "202f30b355f4bfe501292d3c3d650de105a1d7053fcefe875a286e79d3e886e7b005e97255b81f4c35e0ca1ad8e9acc4a57d694828231e57ae7e408e8a2f858a99",
                        "work": "0031b16c3007c425f72c1c32359511fb89ede9980ac807b81f5ab8e5edcce345",
                        "input": "8a023b6abb7e241ad41594fb0a22afb6832e4c4d68bae99707e20bfc8679b8e6",
                        "worker": "STM5gzvDurFRmVUUs38TDtTtGVAEz8TcWMt4xLVbxwP2PP8b9q7P4"
                    },
                    "nonce": 326,
                    "block_id": "00000449f7860b82b4fbe2f317c670e9f01d6d9a",
                    "worker_account": "nxt6"
                }
            ]
        ],
        "signatures": [],
        "ref_block_num": 1097,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_pows'

    worker_account = Column(Unicode(50), nullable=False, index=True)
    block_id = Column(Unicode(40), nullable=False)

    _fields = dict(pow=dict(
        worker_account=lambda x: x.get('worker_account'),
        block_id=lambda x: x.get('block_id')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxTransfer(Base, TxBase):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 4211555470,
        "expiration": "2016-03-25T13:49:33",
        "operations": [
            [
                "transfer",
                {
                    "amount": "833.000 STEEM",
                    "to": "steemit",
                    "memo": "",
                    "from": "admin"
                }
            ]
        ],
        "signatures": [
            "204ffd40d4feefdf309780a62058e7944b6833595c500603f3bb66ddbbca2ea661391196a97aa7dde53fdcca8aeb31f8c63aee4f47a20238f3749d9f4cb77f03f5"
        ],
        "ref_block_num": 25501,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_transfers'

    _from = Column('from', Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    amount = Column(Numeric(15, 6))
    amount_symbol = Column(Unicode(5))
    memo = Column(UnicodeText)

    _fields = dict(transfer=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x['amount']),
        memo=lambda x: x.get('memo'), ))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxTransferFromSavings(Base, TxBase):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 57927444,
        "expiration": "2016-10-11T17:23:06",
        "operations": [
            [
                "transfer_from_savings",
                {
                    "amount": "0.051 STEEM",
                    "to": "knozaki2015",
                    "request_id": 1476206568,
                    "memo": "",
                    "from": "knozaki2015"
                }
            ]
        ],
        "signatures": [
            "205230e01b4def2d4e5a7d0446dd8c41874689155e5c739fc9a6a7d339303a5f135aa89cad21b568ef9f68d15bfaaf85e9fcc78bd544d9831c977a9b1ac578f726"
        ],
        "ref_block_num": 42559,
        "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_transfer_from_savings'

    _from = Column('from', Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    amount = Column(Numeric(15, 6))
    amount_symbol = Column(Unicode(5))
    memo = Column(Unicode(250))
    request_id = Column(Integer)

    _fields = dict(transfer_from_savings=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x['amount']),
        memo=lambda x: x.get('memo'),
        request_id=lambda x: x.get('request_id')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxTransferToSavings(Base, TxBase):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 2803959602,
        "expiration": "2016-10-10T16:41:45",
        "operations": [
            [
                "transfer_to_savings",
                {
                    "amount": "1000.000 SBD",
                    "to": "jamesc",
                    "memo": "",
                    "from": "jamesc"
                }
            ]
        ],
        "signatures": [
            "1f248e64af20e24ad88078b101dba8d565aa1a6bde7ce105bed11a261f5aea9d4b6aca52f3aae23f8b98526ebeede8974407a972a85606036c304020cb2af28afb"
        ],
        "ref_block_num": 12870,
        "extensions": []
    }




    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_transfer_to_savings'

    _from = Column('from', Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    amount = Column(Numeric(15, 6))
    amount_symbol = Column(Unicode(5))
    memo = Column(Unicode(250))

    _fields = dict(transfer_to_savings=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x['amount']),
        memo=lambda x: x.get('memo'), ))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxTransferToVesting(Base, TxBase):
    """Raw Format
    ==========


    {
        "ref_block_prefix": 4131173691,
        "expiration": "2016-03-27T06:55:27",
        "operations": [
            [
                "transfer_to_vesting",
                {
                    "amount": "20.000 STEEM",
                    "to": "itsascam",
                    "from": "james"
                }
            ]
        ],
        "signatures": [
            "1f2853e69b7cf718f53e97c637a348115e17ae3995c773c28445c46b12ccf3716664aca8e82963f343a061ce0e097c29fa3e07ee9dc61d372bb14882b3106547a0"
        ],
        "ref_block_num": 9132,
        "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_transfer_to_vestings'

    _from = Column('from', Unicode(50), index=True)
    to = Column(Unicode(50), index=True)
    amount = Column(Numeric(15, 6))
    amount_symbol = Column(Unicode(5))

    _fields = dict(transfer_to_vesting=dict(
        _from=lambda x: x.get('from'),
        to=lambda x: x.get('to'),
        amount=lambda x: amount_field(x.get('amount'), num_func=float),
        amount_symbol=lambda x: amount_symbol_field(x['amount'])))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxCancelTransferFromSavings(Base, TxBase):
    """Raw Format

    {
        "operations": [
            [
                "cancel_transfer_from_savings",
                {
                    "request_id": 1,
                    "from": "jesta"
                }
            ]
        ],
        "expiration": "2016-09-21T07:55:45",
        "signatures": [
            "1f135b1a9123672cdeb679d57272631858242f569c6066b0f69293963b6b7f7781587478587b843c7f9679855606c37f0ef16707bb03a775d78e2602540626e3d4"
        ],
        "ref_block_num": 45917,
        "ref_block_prefix": 2784823756,
        "extensions": []
    }



    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_cancel_transfer_from_savings'

    _from = Column('from', Unicode(50), index=True)
    request_id = Column(Integer)

    _fields = dict(cancel_transfer_from_savings=dict(
        _from=lambda x: x.get('from'),
        request_id=lambda x: x.get('request_id')))

    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxVote(Base, TxBase):
    """Raw Format
    ==========
    {
    "ref_block_prefix": 286809142,
    "expiration": "2016-12-16T11:31:55",
    "operations": [
        [
            "vote",
            {
                "voter": "a00",
                "weight": 10000,
                "author": "kibbjez",
                "permlink": "t6wv1"
            }
        ]
    ],
    "signatures": [
        "20795b036ba95df0b211bc6e79c3a1d0c2363e694aee62e79eeb60f5ed859d21b86dc2205f28e8779d369a8e9a1c898df0e62efbbaf3fc3ae0ac8c8679ed6b2d68"
    ],
    "ref_block_num": 32469,
    "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 11326766,
        "tx_id": 15964182,
        "voter": "a00",
        "author": "kibbjez",
        "permlink": "t6wv1",
        "weight": 10000
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_votes'

    voter = Column(Unicode(50), nullable=False, index=True)
    author = Column(Unicode(50), nullable=False, index=True)
    permlink = Column(Unicode(512), nullable=False)
    weight = Column(Integer)

    _fields = dict(vote=dict(
        voter=lambda x: x.get('voter'),
        author=lambda x: x.get('author'),
        permlink=lambda x: x.get('permlink'),
        weight=lambda x: x.get('weight')))

    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxWithdrawVestingRoute(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 1734342499,
        "expiration": "2016-07-01T14:12:24",
        "operations": [
            [
                "set_withdraw_vesting_route",
                {
                    "from_account": "lin9uxis",
                    "percent": 10000,
                    "auto_vest": false,
                    "to_account": "linouxis9"
                }
            ]
        ],
        "signatures": [
            "1f1fb84928c952d6bec647f8180787485165714762591096655b9f44ad8b35742a0b964faa5d40b4ff66602ff5e5d978153414abf166adf90b6926e4791164c76a"
        ],
        "ref_block_num": 1756,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 9,
        "tx_id": 454420,
        "from_account": "lin9uxis",
        "to_account": "linouxis9",
        "percent": 10000,
        "auto_vest": False
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_withdraw_vesting_routes'

    from_account = Column(Unicode(50), nullable=False)
    to_account = Column(Unicode(50), nullable=False)
    percent = Column(SmallInteger, nullable=False)
    auto_vest = Column(Boolean)

    _fields = dict(set_withdraw_vesting_route=dict(
        from_account=lambda x: x.get('from_account'),
        to_account=lambda x: x.get('to_account'),
        percent=lambda x: x.get('percent'),
        auto_vest=lambda x: x.get('auto_vest')))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxWithdrawVesting(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 4265937178,
        "expiration": "2016-03-31T18:52:33",
        "operations": [
            [
                "withdraw_vesting",
                {
                    "account": "steemit",
                    "vesting_shares": "260000.000000 VESTS"
                }
            ]
        ],
        "signatures": [
            "2056b5be4b9d12f91e3cec198e74dd048bcfded95b92291709815c0afc069e5aa44c1a62e3aca0001a50d57010a870975c576f83de42e435f8634dcde52a8764c5"
        ],
        "ref_block_num": 7003,
        "extensions": []
    }

    Prepared Format
    ===============
    {
        "id": 2,
        "tx_id": 10275,
        "account": "steemit",
        "vesting_shares": 260000.0000
    }

    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_withdraw_vestings'

    account = Column(Unicode(50), nullable=False)
    vesting_shares = Column(Numeric(25, 6), nullable=False, default=0.0)

    _fields = dict(withdraw_vesting=dict(
        account=lambda x: x.get('account'),
        vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float)))
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


class TxWitnessUpdate(Base, TxBase):
    """Raw Format
    ==========
    {
        "ref_block_prefix": 1306647607,
        "expiration": "2016-04-26T02:53:27",
        "operations": [
            [
                "witness_update",
                {
                    "owner": "arhag",
                    "block_signing_key": "STM5VNk9doxq55YEuyFw6qpNQt7q8neBWHhrau52fjV8N3TjNNUMP",
                    "props": {
                        "account_creation_fee": "100.000 STEEM",
                        "sbd_interest_rate": 1000,
                        "maximum_block_size": 131072
                    },
                    "url": " ",
                    "fee": "0.000 STEEM"
                }
            ]
        ],
        "signatures": [
            "1f2183af215f6878a080b659c4a302ce2c67f0df4c9914872d90cf129e6d1793b11401715e130af0da60f5a5a95c48b8de30140dd9884cbc812a017aab5c2b8b5c"
        ],
        "ref_block_num": 64732,
        "extensions": []
    }


    Args:

    Returns:

    """

    __tablename__ = 'sbds_tx_witness_updates'

    owner = Column(Unicode(50), nullable=False)
    url = Column(Unicode(250), nullable=False)
    block_signing_key = Column(Unicode(64), nullable=False)
    props_account_creation_fee = Column(Numeric(15, 6), nullable=False)
    props_maximum_block_size = Column(Integer, nullable=False)
    props_sbd_interest_rate = Column(Integer, nullable=False)
    fee = Column(Numeric(15, 6), nullable=False, default=0.0)

    _fields = dict(witness_update=dict(
        owner=lambda x: x.get('owner'),
        url=lambda x: x.get('url'),
        block_signing_key=lambda x: x.get('block_signing_key'),
        props_account_creation_fee=lambda x: amount_field(
            x.get('account_creation_fee'), num_func=float, no_value=0),
        props_maximum_block_size=lambda x: get_in(
            ['props', 'maximum_block_size'], x),
        props_sbd_interest_rate=lambda x: get_in(
            ['props', 'sbd_interest_rate'], x),
        fee=lambda x: amount_field(x.get('fee'), num_func=float)
    )
    )
    op_types = tuple(_fields.keys())
    operation_type = Column(Enum(*op_types), nullable=False, index=True)


# These are defined in the steem source code here:
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/operations.hpp
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/steem_operations.hpp
tx_class_map = {
    'account_create': TxAccountCreate,
    'account_create_with_delegation': TxAccountCreateWithDelegation,
    'account_update': TxAccountUpdate,
    'account_witness_proxy': TxAccountWitnessProxy,
    'account_witness_vote': TxAccountWitnessVote,
    'cancel_transfer_from_savings': TxCancelTransferFromSavings,
    'change_recovery_account': TxChangeRecoveryAccount,
    'claim_reward_balance': TxClaimRewardBalance,
    'comment': TxComment,
    'comment_options': TxCommentOption,
    'convert': TxConvert,
    'custom': TxCustom,
    'custom_json': TxCustomJSON,
    'decline_voting_rights': TxDeclineVotingRights,
    'delegate_vesting_shares': TxDelegateVestingShares,
    'delete_comment': TxDeleteComment,
    'escrow_approve': TxEscrowApprove,
    'escrow_dispute': TxEscrowDispute,
    'escrow_release': TxEscrowRelease,
    'escrow_transfer': TxEscrowTransfer,
    'feed_publish': TxFeedPublish,
    'limit_order_cancel': TxLimitOrderCancel,
    'limit_order_create': TxLimitOrderCreate,
    'pow': TxPow,
    'pow2': TxPow2,
    'recover_account': TxRecoverAccount,
    'request_account_recovery': TxRequestAccountRecovery,
    'set_withdraw_vesting_route': TxWithdrawVestingRoute,
    'transfer': TxTransfer,
    'transfer_from_savings': TxTransferFromSavings,
    'transfer_to_savings': TxTransferToSavings,
    'transfer_to_vesting': TxTransferToVesting,
    'vote': TxVote,
    'withdraw_vesting': TxWithdrawVesting,
    'witness_update': TxWitnessUpdate
}
