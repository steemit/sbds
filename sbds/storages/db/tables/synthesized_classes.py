# -*- coding: utf-8 -*-
from copy import deepcopy

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session

import sbds.logging
from sbds.storages.db.tables import Base
from sbds.storages.db.tables.enums import comment_types_enum
from sbds.storages.db.tables.enums import extraction_source_enum
from sbds.storages.db.tables.field_handlers import author
from sbds.storages.db.tables.field_handlers import build_url
from sbds.storages.db.tables.field_handlers import comment_body
from sbds.storages.db.tables.field_handlers import images
from sbds.storages.db.tables.field_handlers import json_metadata
from sbds.storages.db.tables.field_handlers import links
from sbds.storages.db.tables.field_handlers import tags
from sbds.storages.db.tables.field_handlers import post_comment_parent_id
from sbds.storages.db.tables.transaction_classes import TxComment
from sbds.storages.db.utils import UniqueMixin
from sbds.utils import canonicalize_url

logger = sbds.logging.getLogger(__name__)


class SynthBase(UniqueMixin):
    @declared_attr
    def __table_args__(cls):
        args = (
            {
                'mysql_engine': 'InnoDB',
                'mysql_charset': 'utf8mb4',
                'mysql_collate': 'utf8mb4_general_ci'
            },
        )
        return getattr(cls, '__extra_table_args__', tuple()) + args

    def __repr__(self):
        return "<%s (%s)>" % (self.__class__.__name__, self.dump())

    def dump(self):
        data = deepcopy(self.__dict__)
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']
        return data


class Account(Base, SynthBase):
    __tablename__ = 'Accounts'

    name = Column(Unicode(100), primary_key=True)
    json_metadata = Column(UnicodeText)
    created = Column(DateTime(timezone=False))

    post_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    cast_vote_count = Column(Integer, default=0)
    received_vote_count = Column(Integer, default=0)
    witness_vote_count = Column(Integer, default=0)

    _fields = dict(
            name=lambda x: x.get('name'),
            json_metadata=lambda x: json_metadata(x.get('json_metadata')),
            created=lambda x: x.get('created')
    )

    def __repr__(self):
        return "<%s (%s)>" % (self.__class__.__name__, self.name)


    tx_class_account_map = dict(
            TxAccountCreate=('creator','new_account_name'),
            TxAccountRecover=('recovery_account','account_to_recover'),
            TxAccountUpdate='account',
            TxAccountWitnessProxy='account',
            TxAccountWitnessVote=('account','witness'),
            TxAuthorReward='account',
            TxComment=('author','parent_author'),
            TxCommentsOption='author',
            TxConvert='owner',
            TxCurationReward=('curator','comment_author'),
            TxDeleteComment='author',
            TxFeed='publisher',
            TxLimitOrder='owner',
            TxPow='worker_account',
            TxTransfer=('_from','to'),
            TxVote=('voter','author'),
            TxWithdrawVestingRoute=('from_account','to_account'),
            TxWithdraw='account',
            TxWitnessUpdate='owner'
    )


    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return kwargs['name']

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(cls.name == kwargs['name'])


class PostAndComment(Base, SynthBase):
    __tablename__ = 'PostsAndComments'

    id = Column(Integer, primary_key=True)
    tx_comment_id = Column(ForeignKey(TxComment.id,
                                      use_alter=True,
                                      onupdate='CASCADE',
                                      ondelete='CASCADE'), nullable=False, index=True)
    author_name = Column(Unicode(100), ForeignKey(Account.name, use_alter=True), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('PostsAndComments.id', use_alter=True), index=True)

    timestamp = Column(DateTime(timezone=False))
    type = Column(comment_types_enum, nullable=False)

    permlink = Column(Unicode(512), nullable=False, index=True)
    title = Column(Unicode(250))
    body = Column(UnicodeText)
    json_metadata = Column(UnicodeText)

    category = Column(Unicode(300))
    url = Column(Unicode(500))
    length = Column(Integer)

    language = Column(Unicode(40))

    children = relationship('PostAndComment', backref=backref('parent', remote_side=[id]))

    _fields = dict(
            tx_comment_id=lambda x: x.get('id'),
            author_name=lambda x: author(context=x,
                                         author_name=x.get('author_name'),
                                         session=x.get('session')),
            parent_id=lambda x: post_comment_parent_id(context=x, session=x.get('session')),
            timestamp=lambda x: x.get('timestamp'),
            type=lambda x: x.get('type'),
            permlink=lambda x: x.get('permlink'),
            title=lambda x: x.get('title'),
            body=lambda x: comment_body(x.get('body')),
            json_metadata=lambda x: x.get('json_metadata'),
            category=lambda x: x.get('parent_permlink'),
            url=lambda x: build_url(context=x),
            length=lambda x: len(x.get('body')),
            images=lambda x: images(context=x,
                                    meta=x.get('json_metadata'),
                                    body=x.get('body'),
                                    session=x.get('session')),
            links=lambda x: links(context=x,
                                  meta=x.get('json_metadata'),
                                  body=x.get('body'),
                                  session=x.get('session')),
            tags=lambda x: tags(context=x,
                                meta=x.get('json_metadata'),
                                session=x.get('session')
                                )
    )

    @classmethod
    def from_tx(cls, txcomment, **kwargs):
        data_dict = deepcopy(txcomment.__dict__)
        session = object_session(txcomment)
        data_dict['timestamp'] = txcomment.transaction.block.timestamp
        data_dict['tx_comment_id'] = txcomment.id
        data_dict['type'] = txcomment.type
        data_dict['txcomment'] = txcomment
        data_dict['session'] = session
        prepared = cls._prepare_for_storage(data_dict=data_dict)
        return cls(**prepared)

    @classmethod
    def _prepare_for_storage(cls, **kwargs):
        data_dict = kwargs['data_dict']
        try:
            prepared = {k: v(data_dict) for k, v in cls._fields.items()}
            return prepared
        except Exception as e:
            extra = dict(_fields=cls._fields, error=e, **kwargs)
            logger.error(e, extra=extra)
            return None

    __mapper_args__ = {
        'polymorphic_on': type
    }

    def __repr__(self):
        return "<%s (id=%s author=%s title=%s)>" % (
            self.__class__.__name__,
            self.id,
            self.author_name,
            self.title)

    @classmethod
    def unique_hash(cls, tx_comment_id):
        return tx_comment_id

    @classmethod
    def unique_filter(cls, query, tx_comment_id):
        return query.filter(cls.tx_comment_id == tx_comment_id)



class Post(PostAndComment):
    author = relationship('Account', backref='posts')
    txcomment = relationship('TxComment', backref='posts')
    tags = relationship("Tag", secondary='sbds_tag_table', backref='posts')

    __mapper_args__ = {
        'polymorphic_identity': 'post'
    }


class Comment(PostAndComment):
    author = relationship('Account', backref='comments')
    txcomment = relationship('TxComment')
    tags = relationship("Tag", secondary='sbds_tag_table', backref='comments')

    __mapper_args__ = {
        'polymorphic_identity': 'comment'
    }


class Tag(Base, SynthBase):
    __tablename__ = 'Tags'

    _id = Column(Unicode(50), primary_key=True)

    @hybrid_property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_string):
        self._id = self.format_id_string(id_string)

    @classmethod
    def format_id_string(cls, id_string):
        return id_string.strip().lower()

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return cls.format_id_string(kwargs['id'])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        id_string = cls.format_id_string(kwargs['id'])
        return query.filter(cls.id==id_string)




class Link(Base, SynthBase):
    __tablename__ = 'Links'

    id = Column(Integer, primary_key=True)
    _url = Column(Unicode(250), index=True)
    pac_id = Column(Integer, ForeignKey('PostsAndComments.id'))
    extraction_source = Column(extraction_source_enum, nullable=False)
    body_offset = Column(Integer)

    post_and_comment = relationship('PostAndComment', backref='links')

    @hybrid_property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        canonical_url = canonicalize_url(url)
        if not canonical_url:
            raise ValueError('bad url %s', url)
        else:
            self._url = canonical_url

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        url = canonicalize_url(kwargs['url'])
        pac_id = kwargs.get('pac_id')
        return tuple([pac_id, url])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        url = canonicalize_url(kwargs['url'])
        pac_id = kwargs.get('pac_id')
        return query.filter(cls.pac_id == pac_id, cls._url == url)


class Image(Base, SynthBase):
    __tablename__ = 'Images'

    id = Column(Integer, primary_key=True)
    _url = Column(Unicode(250), index=True)
    inline = Column(Boolean)
    inline_data = Column(UnicodeText)
    pac_id = Column(Integer, ForeignKey(PostAndComment.id))
    extraction_source = Column(extraction_source_enum)

    post_and_comment = relationship('PostAndComment', backref='images')

    @hybrid_property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        canonical_url = canonicalize_url(url)
        if not canonical_url:
            raise ValueError('bad url', extra=dict(url=url))
        else:
            self._url = canonical_url

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        url = canonicalize_url(kwargs['url'])
        pac_id = kwargs.get('pac_id')
        return tuple([pac_id, url])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        url = canonicalize_url(kwargs['url'])
        pac_id = kwargs.get('pac_id')
        return query.filter(cls.pac_id == pac_id, cls._url == url)


tag_table = Table('sbds_tag_table', Base.metadata,
                  Column('post_and_comment_id',
                         Integer,
                         ForeignKey(PostAndComment.id),
                         nullable=False),
                  Column('tag_id',
                         Unicode(50),
                         ForeignKey(Tag.id),
                         nullable=False),
                  mysql_charset='utf8mb4',
                  mysql_engine='innodb',
                  mysql_collate='utf8mb4_general_ci')
