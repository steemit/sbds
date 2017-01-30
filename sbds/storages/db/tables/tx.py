# -*- coding: utf-8 -*-
from copy import deepcopy

from toolz.dicttoolz import get_in

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import SmallInteger

from sqlalchemy import Boolean
from sqlalchemy import UnicodeText
from sqlalchemy import Unicode

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

import sbds.logging

from ..utils import UniqueMixin

from .core import extract_operations_from_block

from ..field_handlers import amount_field
from ..field_handlers import amount_symbol_field
from ..field_handlers import comment_body_field
from ..field_handlers import json_metadata_field

from .core import Base
from .core import Transaction


logger = sbds.logging.getLogger(__name__)


class TxBase(UniqueMixin):
    @declared_attr
    def __table_args__(cls):
        args = (
            Index('sbds_ix_unique_%s' % cls.__tablename__, 'tx_id', 'transaction_num', 'operation_num', unique=True),
            {
                'mysql_engine': 'InnoDB',
                'mysql_charset': 'utf8mb4',
                'mysql_collate': 'utf8mb4_general_ci'
            }
        )
        return getattr(cls, '__extra_table_args__', tuple()) + args

    id = Column(Integer, primary_key=True)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)

    @declared_attr
    def tx_id(cls):
        return Column(Integer, ForeignKey(Transaction.tx_id,
                                          use_alter=True,
                                          onupdate='CASCADE',
                                          ondelete='CASCADE'),
                      nullable=False,
                      index=True)

    _fields = dict()

    @classmethod
    def _prepare_for_storage(cls, **kwargs):
        data_dict = kwargs['data_dict']
        op_type = data_dict['type']
        tx_cls = cls.tx_class_for_type(op_type)
        _fields = tx_cls._fields.get(op_type)
        try:
            prepared = {k: v(data_dict) for k, v in _fields.items()}
            prepared['transaction_num'] = data_dict['transaction_num']
            prepared['operation_num'] = data_dict['operation_num']
            if 'transaction_obj' in kwargs:
                prepared['transaction'] = kwargs['transaction_obj']

            elif 'tx_id' in kwargs:
                prepared['tx_id'] = kwargs['tx_id']
            return prepared
        except Exception as e:
            extra = dict(op_type=op_type, vivi_dict=data_dict, _fields=_fields, error=e, **kwargs)
            logger.error(e, extra=extra)
            return None

    @classmethod
    def from_raw_block(cls, raw_block, transactions=None, session=None):
        operations = list(extract_operations_from_block(raw_block))
        logger.debug('extracted %s operations from transaction', len(operations))
        if transactions:
            for op in operations:
                op['transaction_obj'] = transactions[op['transaction_num'] - 1]
        prepared = [cls._prepare_for_storage(data_dict=d) for d in operations]
        objs = []
        for i, prepared_tx in enumerate(prepared):
            op_type = operations[i]['type']
            tx_cls = cls.tx_class_for_type(op_type)
            logger.debug('operation type %s mapped to class %s',
                         op_type, tx_cls.__name__)
            objs.append(tx_cls(**prepared_tx))
        logger.debug('instantiated: %s', [o.__class__.__name__ for o in objs])
        return objs

    @classmethod
    def tx_class_for_type(cls, tx_type):
        return tx_class_map[tx_type]

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return tuple([kwargs['tx_id'],
                      kwargs['transaction_num'],
                      kwargs['operation_num']])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(cls.transaction_num == kwargs['transaction_num'],
                            cls.operation_num == kwargs['operation_num'],
                            cls.tx_id == kwargs['tx_id'])

    def __repr__(self):
        return "<%s (transaction_num: %s operation_num: %s keys: %s)>" % (
            self.__class__.__name__,
            self.transaction_num,
            self.operation_num,
            tuple(self.dump().keys())
        )

    def dump(self):
        data = deepcopy(self.__dict__)
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']
        return data


class TxAccountCreate(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_account_creates'

    fee = Column(Numeric(15, 4), nullable=False)
    creator = Column(Unicode(50), nullable=False, index=True)
    new_account_name = Column(Unicode(50))
    owner_key = Column(Unicode(80), nullable=False)
    active_key = Column(Unicode(80), nullable=False)
    posting_key = Column(Unicode(80), nullable=False)
    memo_key = Column(Unicode(250), nullable=False)
    json_metadata = Column(UnicodeText)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(account_create=
    dict(
            creator=lambda x: x.get('creator'),
            fee=lambda x: amount_field(x.get('fee'), num_func=float),
            new_account_name=lambda x: x.get('new_account_name'),
            memo_key=lambda x: x.get('memo_key'),
            json_metadata=lambda x: json_metadata_field(x.get('json_metadata')),
            owner_key=lambda x: get_in(['owner', 'key_auths', 0, 0], x),
            active_key=lambda x: get_in(['active', 'key_auths', 0, 0], x),
            posting_key=lambda x: get_in(['posting', 'key_auths', 0, 0], x)
    )
    )
    op_types = tuple(_fields.keys())


class TxAccountRecover(Base, TxBase):
    """
    Raw Format
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

    op_type==recover_account
    ========================
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


    Prepared Format
    ===============
    {
        "tx_id": 1069359,
        "recovery_account": "steem",
        "account_to_recover": "gandalf",
        "recovered": False
    }
    """

    __tablename__ = 'sbds_tx_account_recovers'

    recovery_account = Column(Unicode(50))
    account_to_recover = Column(Unicode(50), nullable=False)
    recovered = Column(Boolean, default=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(
            recover_account=dict(
                    recover_account=lambda x: x.get('recovery_account'),
                    account_to_recover=lambda x: x.get('account_to_recover'),
                    recovered=True),
            request_account_recovery=dict(
                    operation_num=lambda x: x.get('operation_num'),
                    recover_account=lambda x: x.get('recovery_account'),
                    account_to_recover=lambda x: x.get('account_to_recover'),
                    recovered=False)
    )
    op_types = tuple(_fields.keys())


class TxAccountUpdate(Base, TxBase):
    """
    Raw Format
    ==========
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

    Prepared Format
    ===============
    {
        "id": 4,
        "tx_id": 44188,
        "account": "theoretical",
        "key_auth1": null,
        "key_auth2": null,
        "memo_key": "STM6FATHLohxTN8RWWkU9ZZwVywXo6MEDjHHui1jEBYkG2tTdvMYo",
        "json_metadata": ""
    }
    """

    __tablename__ = 'sbds_tx_account_updates'

    account = Column(Unicode(50))
    key_auth1 = Column(Unicode(80))
    key_auth2 = Column(Unicode(80))
    memo_key = Column(Unicode(250), nullable=False)
    json_metadata = Column(UnicodeText)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(account_update=
    dict(
            account=lambda x: x.get('account'),
            key_auth1=lambda x: None,  # TODO fix null
            key_auth2=lambda x: None,  # TODO fix null
            memo_key=lambda x: x.get('memo_key'),
            json_metadata=lambda x: json_metadata_field(x.get('json_metadata')),
    ))
    op_types = tuple(_fields.keys())


class TxAccountWitnessProxy(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_account_witness_proxies'

    account = Column(Unicode(50), nullable=False)
    Proxy = Column(Unicode(50), nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(account_witness_proxy=
    dict(
            account=lambda x: x.get('account'),
            Proxy=lambda x: x.get('proxy'),  # TODO fix capitalization
    )
    )
    op_types = tuple(_fields.keys())


class TxAccountWitnessVote(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_account_witness_votes'

    account = Column(Unicode(50), nullable=False)
    witness = Column(Unicode(50), nullable=False)
    approve = Column(Boolean, default=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(account_witness_vote=
    dict(
            account=lambda x: x.get('account'),
            approve=lambda x: x.get('appove'),
            witness=lambda x: x.get('witness')
    )
    )
    op_types = tuple(_fields.keys())


class TxAuthorReward(Base, TxBase):
    """
    NONE
    Raw Format
    ==========

    Prepared Format
    ===============
    """

    __tablename__ = 'sbds_tx_author_rewards'

    author = Column(Unicode(50), nullable=False)
    permlink = Column(Unicode(512), nullable=False)
    sdb_payout = Column(Numeric(15, 4), nullable=False)
    steem_payout = Column(Numeric(15, 4), nullable=False)
    vesting_payout = Column(Numeric(15, 4), nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict()
    op_types = tuple(_fields.keys())


class TxComment(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_comments'

    author = Column(Unicode(50), nullable=False, index=True)
    permlink = Column(Unicode(512), nullable=False, index=True)
    parent_author = Column(Unicode(50))
    parent_permlink = Column(Unicode(512))
    title = Column(Unicode(250))
    body = Column(UnicodeText)
    json_metadata = Column(UnicodeText)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(comment=
    dict(
            author=lambda x: x.get('author'),
            permlink=lambda x: x.get('permlink'),
            parent_author=lambda x: x.get('parent_author'),
            parent_permlink=lambda x: x.get('parent_permlink'),
            title=lambda x: x.get('title'),
            body=lambda x: comment_body_field(x['body']),
            json_metadata=lambda x: json_metadata_field(x.get('json_metadata')),
    )
    )
    op_types = tuple(_fields.keys())

    @classmethod
    def find_parent_from_prepared(cls, session, prepared):
        return session.query(cls).filter(cls.parent_permlink == prepared['parent_permlink'],
                                         cls.parent_author == prepared['parent_author']).one_or_none()

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


class TxCommentsOption(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_comments_options'

    author = Column(Unicode(50), nullable=False)
    permlink = Column(Unicode(512), nullable=False)
    max_accepted_payout = Column(Numeric(15, 4), nullable=False)
    percent_steem_dollars = Column(SmallInteger, default=0)
    allow_votes = Column(Boolean, nullable=False)
    allow_curation_rewards = Column(Boolean, nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(comment_options=dict(
            author=lambda x: x.get('author'),
            permlink=lambda x: x.get('permlink'),
            max_accepted_payout=lambda x: amount_field(x.get('max_accepted_payout'), num_func=float),
            percent_steem_dollars=lambda x: x.get('percent_steem_dollars'),
            allow_votes=lambda x: x.get('allow_votes'),
            allow_curation_rewards=lambda x: x.get('allow_curation_rewards')
    )
    )
    op_types = tuple(_fields.keys())


class TxConvert(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_converts'

    owner = Column(Unicode(50), nullable=False)
    requestid = Column(BigInteger, nullable=False)
    amount = Column(Numeric(15, 4), nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(convert=
    dict(
            owner=lambda x: x.get('owner'),
            amount=lambda x: amount_field(x.get('amount'), num_func=float),
            requestid=lambda x: x.get('requestid')
    )
    )
    op_types = tuple(_fields.keys())


class TxCurationReward(Base, TxBase):
    """
    NONE
    Raw Format
    ==========

    Prepared Format
    ===============
    """

    __tablename__ = 'sbds_tx_curation_rewards'

    curator = Column(Unicode(50), nullable=False)
    comment_author = Column(Unicode(50), nullable=False)
    comment_permlink = Column(Unicode(512), nullable=False)
    reward = Column(Unicode(50), nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict()
    op_types = tuple(_fields.keys())


class TxCustom(Base, TxBase):
    """
    Raw Format
    ==========
    {
        "ref_block_prefix": 1654024379,
        "expiration": "2016-06-03T18:37:24",
        "operations": [
            [
                "custom_json",
                {
                    "required_posting_auths": [
                        "steemit"
                    ],
                    "required_auths": [],
                    "id": "follow",
                    "json": "{\"follower\":\"steemit\",\"following\":\"steem\",\"what\":[\"posts\"]}"
                }
            ]
        ],
        "signatures": [
            "1f6019603d73f8c26b92cbdf1c224bf48fb0e600ff9e1689a09e8e4cb1234aeeb92b5eb6f8b8d148bbd3e62a4eb2bc94d1ff2293ec9b957d17d46e9dc11f41735d"
        ],
        "ref_block_num": 56232,
        "extensions": []
    }


    Prepared Format
    ===============
    {
        "id": 1,
        "tx_id": 294602,
        "tid": "follow",
        "json_metadata": "{\"follower\":\"steemit\",\"following\":\"steem\",\"what\":[\"posts\"]}"
    }
    """

    __tablename__ = 'sbds_tx_customs'

    tid = Column(Unicode(50), nullable=False)
    json_metadata = Column(UnicodeText)

    transaction = relationship('Transaction', backref=__tablename__)

    common = dict(
            tid=lambda x: x.get('id'),
            json_metadata=lambda x: json_metadata_field(x.get('json'))
    )
    _fields = dict(custom=common,
                   custom_json=common)
    op_types = tuple(_fields.keys())


class TxDeleteComment(Base, TxBase):
    """
    Raw Format
    ==========
    {
        "ref_block_prefix": 3023139187,
        "expiration": "2016-06-06T19:34:27",
        "operations": [
            [
                "delete_comment",
                {
                    "author": "jsc",
                    "permlink": "test-delete"
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
        "permlink": "test-delete"
    }
    """

    __tablename__ = 'sbds_tx_delete_comments'

    author = Column(Unicode(50), nullable=False)
    permlink = Column(Unicode(250), nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(delete_comment=dict(
            author=lambda x: x.get('author'),
            permlink=lambda x: x.get('permlink')
    )
    )
    op_types = tuple(_fields.keys())


class TxFeed(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_feeds'

    publisher = Column(Unicode(50), nullable=False)
    exchange_rate_base = Column(Numeric(15, 4), nullable=False)
    exchange_rate_quote = Column(Numeric(15, 4), nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(feed_publish=
    dict(
            publisher=lambda x: x.get('publisher'),
            exchange_rate_base=lambda x: amount_field(get_in(['exchange_rate', 'base'], x), num_func=float),
            exchange_rate_quote=lambda x: amount_field(get_in(['exchange_rate', 'quote'], x), num_func=float)
    )
    )
    op_types = tuple(_fields.keys())


class TxLimitOrder(Base, TxBase):
    """
    Raw Format
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

    Prepared Format
    ===============
    {
        "id": 47,
        "tx_id": 454081,
        "owner": "adm",
        "orderid": 9,
        "cancel": False,
        "amount_to_sell": 5.0000,
        "min_to_receive": 1.5420,
        "fill_or_kill": False,
        "expiration": "2016-07-01 13:34:03.000"
    }
    """

    __tablename__ = 'sbds_tx_limit_orders'

    owner = Column(Unicode(50), nullable=False)
    orderid = Column(BigInteger, nullable=False)
    cancel = Column(Boolean, default=False)
    amount_to_sell = Column(Numeric(15, 4))
    # sell_symbol = Column(Unicode(5))
    min_to_receive = Column(Numeric(15, 4))
    # receive_symbol = Column(Unicode(5))
    fill_or_kill = Column(Boolean, default=False)
    expiration = Column(DateTime)

    transaction = relationship('Transaction', backref=__tablename__)

    common = dict(
            owner=lambda x: x.get('owner'),
            orderid=lambda x: x.get('orderid'),
            cancel=lambda x: x.get('cancel'),
            amount_to_sell=lambda x: amount_field(x.get('amount_to_sell'), num_func=float),
            # sell_symbol=lambda x: x['amount_to_sell'].split()[1],
            min_to_receive=lambda x: amount_field(x.get('min_to_receive'), num_func=float),
            # receive_symbol=lambda x: x['min_to_receive'].split()[1],
            fill_or_kill=lambda x: x.get('fill_or_kill'),
            expiration=lambda x: x.get('expiration')
    )
    _fields = dict(limit_order_create=common,
                   limit_order_cancel=dict(
                           owner=lambda x: x.get('owner'),
                           orderid=lambda x: x.get('orderid')))
    op_types = tuple(_fields.keys())


class TxPow(Base, TxBase):
    """
    Raw Format
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

    op_type=='pow2'
    ==============
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

    Prepared Format
    ===============

    op_type=='pow'
    ==============
    {
        "id": 1,
        "tx_id": 1,
        "worker_account": "admin",
        "block_id": "000004433bd4602cf5f74dbb564183837df9cef8"
    }

    op_type=='pow2'
    ==============
    {
        "id": 412175,
        "tx_id": 19098700,
        "worker_account": "nori",
        "block_id": "8646730"
    }
    """

    __tablename__ = 'sbds_tx_pows'

    worker_account = Column(Unicode(50), nullable=False, index=True)
    block_id = Column(Unicode(40), nullable=False)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(pow=dict(worker_account=lambda x: x.get('worker_account'),
                            block_id=lambda x: x.get('block_id')),
                   pow2=dict(worker_account=lambda x: get_in(['work', 1, 'input', 'worker_account'], x),
                             block_id=lambda x: get_in(['work', 1, 'input', 'prev_block'], x))
                   )
    op_types = tuple(_fields.keys())


class TxTransfer(Base, TxBase):
    """
    Raw Format
    ==========

    op_type==tranfer
    ================
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

    op_type==transfer_from_savings
    ==============================
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

    op_type==transfer_to_savings
    ============================
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


    op_type==transfer_to_vesting
    ============================
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

     op_type==cancel_transfer_from_savings
    ============================
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


    Prepared Format
    ===============
    {
        "id": 49,
        "tx_id": 3652,
        "type": "transfer_to_vesting",
        "from": "james",
        "to": "itsascam",
        "amount": 20.0000,
        "amount_symbol": "STEEM",
        "memo": null,
        "request_id": 0
    }
    """

    __tablename__ = 'sbds_tx_transfers'

    type = Column(Unicode(50), nullable=False, index=True)
    _from = Column('from', Unicode(50), nullable=False, index=True)
    to = Column(Unicode(50), nullable=False, index=True)
    amount = Column(Numeric(15, 4), nullable=False)
    amount_symbol = Column(Unicode(5))
    memo = Column(Unicode(250))
    request_id = Column(Integer)

    transaction = relationship('Transaction', backref=__tablename__)

    _common = dict(
            type=lambda x: x.get('type'),
            _from=lambda x: x.get('from'),
            to=lambda x: x.get('to'),
            amount=lambda x: amount_field(x.get('amount'), num_func=float),
            amount_symbol=lambda x: amount_symbol_field(x['amount']),
            memo=lambda x: x.get('memo'),
            request_id=lambda x: x.get('request_id')
    )

    _cancel_transfer_from_savings_fields = _common.copy()
    _cancel_transfer_from_savings_fields['amount'] = lambda x: None
    _cancel_transfer_from_savings_fields['amount_symbol'] = lambda x: None

    _fields = dict(transfer=_common,
                   transfer_from_savings=_common,
                   transfer_to_savings=_common,
                   transfer_to_vesting=_common,
                   cancel_transfer_from_savings=_cancel_transfer_from_savings_fields
                   )
    op_types = tuple(_fields.keys())


class TxVote(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_votes'
    __extra_table_args__ = (Index('ix_txvotes_id_author', 'voter', 'tx_id', 'author'),)

    voter = Column(Unicode(50), nullable=False, index=True)
    author = Column(Unicode(50), nullable=False, index=True)
    permlink = Column(Unicode(512), nullable=False)
    weight = Column(Integer)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(vote=dict(
            voter=lambda x: x.get('voter'),
            author=lambda x: x.get('author'),
            permlink=lambda x: x.get('permlink'),
            weight=lambda x: x.get('weight')
    )
    )

    op_types = tuple(_fields.keys())


class TxWithdrawVestingRoute(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_withdraw_vesting_routes'

    from_account = Column(Unicode(50), nullable=False)
    to_account = Column(Unicode(50), nullable=False)
    percent = Column(SmallInteger, nullable=False)
    auto_vest = Column(Boolean)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(set_withdraw_vesting_route=dict(
            from_account=lambda x: x.get('from_account'),
            to_account=lambda x: x.get('to_account'),
            percent=lambda x: x.get('percent'),
            auto_vest=lambda x: x.get('auto_vest')
    )
    )
    op_types = tuple(_fields.keys())


class TxWithdraw(Base, TxBase):
    """
    Raw Format
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
    """

    __tablename__ = 'sbds_tx_withdraws'

    account = Column(Unicode(50), nullable=False)
    vesting_shares = Column(Numeric(15, 4), nullable=False, default=0.0)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(withdraw_vesting=dict(
            account=lambda x: x.get('account'),
            vesting_shares=lambda x: amount_field(x.get('vesting_shares'), num_func=float)
    )
    )
    op_types = tuple(_fields.keys())


class TxWitnessUpdate(Base, TxBase):
    """
    Raw Format
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

    Prepared Format
    ===============
    {
        "id": 1,
        "tx_id": 102103,
        "owner": "steempty",
        "url": "fmooo/steemd-docker",
        "block_signing_key": "STM8LoQjQqJHvotqBo7HjnqmUbFW9oJ2theyqonzUd9DdJ7YYHsvD",
        "props_account_creation_fee": 100.0000,
        "props_maximum_block_size": 131072,
        "props_sbd_interest_rate": 1000,
        "fee": 0.0000
    }
    """

    __tablename__ = 'sbds_tx_witness_updates'

    owner = Column(Unicode(50), nullable=False)
    url = Column(Unicode(250), nullable=False)
    block_signing_key = Column(Unicode(64), nullable=False)
    props_account_creation_fee = Column(Numeric(15, 4), nullable=False)
    props_maximum_block_size = Column(Integer, nullable=False)
    props_sbd_interest_rate = Column(Integer, nullable=False)
    fee = Column(Numeric(15, 4), nullable=False, default=0.0)

    transaction = relationship('Transaction', backref=__tablename__)

    _fields = dict(witness_update=dict(
            owner=lambda x: x.get('owner'),
            url=lambda x: x.get('url'),
            block_signing_key=lambda x: x.get('block_signing_key'),
            props_account_creation_fee=lambda x: amount_field(x.get('account_creation_fee'), num_func=float, no_value=0),
            props_maximum_block_size=lambda x: get_in(['props', 'maximum_block_size'], x),
            props_sbd_interest_rate=lambda x: get_in(['props', 'sbd_interest_rate'], x),
            fee=lambda x: amount_field(x.get('fee'), num_func=float)
    )
    )
    op_types = tuple(_fields.keys())


tx_class_map = {
    'account_create': TxAccountCreate,
    'account_update': TxAccountUpdate,
    'account_witness_proxy': TxAccountWitnessProxy,
    'account_witness_vote': TxAccountWitnessVote,
    'cancel_transfer_from_savings': TxTransfer,
    'change_recovery_account': TxAccountUpdate,
    'comment': TxComment,
    'comment_options': TxCommentsOption,
    'convert': TxConvert,
    'custom': TxCustom,
    'custom_json': TxCustom,
    'delete_comment': TxDeleteComment,
    'feed_publish': TxFeed,
    'limit_order_cancel': TxLimitOrder,
    'limit_order_create': TxLimitOrder,
    'pow': TxPow,
    'pow2': TxPow,
    'recover_account': TxAccountRecover,
    'request_account_recovery': TxAccountRecover,
    'set_withdraw_vesting_route': TxWithdrawVestingRoute,
    'transfer': TxTransfer,
    'transfer_from_savings': TxTransfer,
    'transfer_to_savings': TxTransfer,
    'transfer_to_vesting': TxTransfer,
    'vote': TxVote,
    'withdraw_vesting': TxWithdraw,
    'witness_update': TxWitnessUpdate
}
