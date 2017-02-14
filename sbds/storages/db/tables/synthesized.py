# -*- coding: utf-8 -*-
from copy import deepcopy

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy import and_
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session

import sbds.logging
from sbds.storages.db.enums import comment_types_enum
from sbds.storages.db.enums import extraction_source_enum
from sbds.storages.db.field_handlers import author_field
from sbds.storages.db.field_handlers import comment_body_field
from sbds.storages.db.field_handlers import comment_parent_id_field
from sbds.storages.db.field_handlers import has_patch_field
from sbds.storages.db.field_handlers import images_field
from sbds.storages.db.field_handlers import language_field
from sbds.storages.db.field_handlers import links_field
from sbds.storages.db.field_handlers import tags_field
from sbds.storages.db.field_handlers import url_field
from sbds.storages.db.tables import Base
from sbds.storages.db.utils import UniqueMixin
from sbds.utils import canonicalize_url

logger = sbds.logging.getLogger(__name__)


# noinspection PyMethodParameters
class SynthBase(UniqueMixin):
    # pylint: disable=unused-argument

    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError

    # pylint: enable=unused-argument

    # pylint: disable=no-self-argument
    @declared_attr
    def __table_args__(cls):
        args = ({
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_general_ci'
        }, )
        return getattr(cls, '__extra_table_args__', tuple()) + args

    # pylint: enable=no-self-argument

    def __repr__(self):
        return "<%s (%s)>" % (self.__class__.__name__, self.dump())

    def dump(self):
        data = deepcopy(self.__dict__)
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']
        return data


class Account(Base, SynthBase):
    __tablename__ = 'sbds_syn_accounts'

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
        json_metadata=lambda x: x.get('json_metadata'),
        created=lambda x: x.get('created'))

    def __repr__(self):
        return "<%s (%s)>" % (self.__class__.__name__, self.name)

    tx_class_account_map = dict(
        TxAccountCreate=('creator', 'new_account_name'),
        TxAccountRecover=('recovery_account', 'account_to_recover'),
        TxAccountUpdate='account',
        TxAccountWitnessProxy='account',
        TxAccountWitnessVote=('account', 'witness'),
        TxAuthorReward='account',
        TxComment=('author', 'parent_author'),
        TxCommentsOption='author',
        TxConvert='owner',
        TxCurationReward=('curator', 'comment_author'),
        TxDeleteComment='author',
        TxFeed='publisher',
        TxLimitOrder='owner',
        TxPow='worker_account',
        TxTransfer=('_from', 'to'),
        TxVote=('voter', 'author'),
        TxWithdrawVestingRoute=('from_account', 'to_account'),
        TxWithdraw='account',
        TxWitnessUpdate='owner')

    # pylint: disable=unused-argument
    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return kwargs['name']

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        return query.filter(cls.name == kwargs['name'])

    # pylint: enable=unused-argument

    @classmethod
    def from_tx(cls, tx_obj):
        return dict(name=tx_obj.new_account_name, created=tx_obj.timestamp)

    @classmethod
    def add_missing(cls, sessionmaker):
        from .tx import TxAccountCreate
        session1 = sessionmaker()
        session2 = sessionmaker()
        q = session1.query(TxAccountCreate.new_account_name,
                           TxAccountCreate.timestamp) \
            .outerjoin(Account,
                       TxAccountCreate.new_account_name == Account.name) \
            .filter(Account.name.is_(None))

        for tx in q.yield_per(1000):
            prepared = cls.from_tx(tx)
            logger.debug('%s.add_missing: tx: %s prepared:%s', cls.__name__,
                         tx, prepared)
            result = cls.as_unique(session2, **prepared)
            logger.debug('%s.add_missing result: %s', cls.__name__, result)


class PostAndComment(Base, SynthBase):
    __tablename__ = 'sbds_syn_posts_and_comments'
    __extra_table_args__ = (UniqueConstraint(
        'block_num',
        'transaction_num',
        'operation_num',
        name='ix_sbds_syn_posts_and_comments_unique_1'), Index(
            'ix_sbds_syn_posts_and_comments_body_fulltext',
            'body',
            mysql_prefix='FULLTEXT'), ForeignKeyConstraint(
                ['block_num', 'transaction_num', 'operation_num'], [
                    'sbds_tx_comments.block_num',
                    'sbds_tx_comments.transaction_num',
                    'sbds_tx_comments.operation_num'
                ],
                name='ix_sbds_syn_posts_and_comments_ibfk_4'), )
    id = Column(Integer, primary_key=True)
    block_num = Column(Integer, nullable=False)
    transaction_num = Column(SmallInteger, nullable=False)
    operation_num = Column(SmallInteger, nullable=False)

    author_name = Column(
        Unicode(100),
        ForeignKey(Account.name, use_alter=True),
        nullable=False,
        index=True)
    parent_id = Column(
        Integer,
        ForeignKey('sbds_syn_posts_and_comments.id', use_alter=True),
        index=True)  # TODO remove tablename reference

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
    has_patch = Column(Boolean)

    children = relationship(
        'PostAndComment', backref=backref('parent', remote_side=[id]))

    _fields = dict(
        block_num=lambda x: x.get('block_num'),
        transaction_num=lambda x: x.get('transaction_num'),
        operation_num=lambda x: x.get('operation_num'),
        author_name=lambda x: author_field(context=x,
                                           author_name=x.get('author'),
                                           session=x.get('session')),
        parent_id=lambda x: comment_parent_id_field(context=x,
                                                    session=x.get(
                                                        'session')),
        timestamp=lambda x: x.get('timestamp'),
        type=lambda x: x.get('type'),
        permlink=lambda x: x.get('permlink'),
        title=lambda x: x.get('title'),
        body=lambda x: comment_body_field(x.get('body')),
        json_metadata=lambda x: x.get('json_metadata'),
        category=lambda x: x.get('parent_permlink'),
        url=lambda x: url_field(context=x),
        length=lambda x: len(x.get('body')),
        images=lambda x: images_field(meta=x.get('json_metadata')),
        links=lambda x: links_field(meta=x.get('json_metadata')),
        tags=lambda x: tags_field(meta=x.get('json_metadata'),
                                  session=x.get('session')),
        language=lambda x: language_field(x.get('body')),
        has_patch=lambda x: has_patch_field(x.get('body'))

    )

    @classmethod
    def prepare_from_tx(cls, txcomment, session=None):
        """returns fields key value dict

        Args:
          session: param txcomment: TxComment instance (Default value = None)
          kwargs: return: dict
          txcomment:
          **kwargs:

        Returns:
          dict

        """

        data_dict = deepcopy(txcomment.__dict__)
        data_dict['block_num'] = txcomment.block_num
        data_dict['transaction_num'] = txcomment.transaction_num
        data_dict['operation_num'] = txcomment.operation_num
        data_dict['timestamp'] = txcomment.timestamp
        data_dict['type'] = txcomment.type
        data_dict['txcomment'] = txcomment
        data_dict['session'] = session or object_session(txcomment)
        prepared = cls._prepare_for_storage(data_dict=data_dict)
        return prepared

    @classmethod
    def from_tx(cls, txcomment, session=None, **kwargs):
        """returns Post or Comment instance

        Args:
          txcomment: param session:
          kwargs: return:  Post | Comment
          session:  (Default value = None)
          **kwargs:

        Returns:
          Post | Comment

        """
        if txcomment.is_comment:
            obj_cls = Comment
            cls_name = 'Comment'
        elif txcomment.is_post:
            obj_cls = Post
            cls_name = 'Post'
        else:
            raise ValueError('txcomment must by either post or comment')
        prepared = cls.prepare_from_tx(txcomment, session=session, **kwargs)
        logger.debug('%s.add: tx: %s prepared:%s', cls_name, txcomment,
                     prepared)
        return obj_cls(**prepared)

    @classmethod
    def as_unique_from_tx(cls, txcomment, session=None, **kwargs):
        """returns unique Post or Comment instance

        Args:
          txcomment: param session:
          kwargs: return:
          session:  (Default value = None)
          **kwargs:

        Returns:

        """
        prepared = cls.prepare_from_tx(txcomment, session=session, **kwargs)
        if txcomment.is_comment:
            obj_cls = Comment
        elif txcomment.is_post:
            obj_cls = Post
        else:
            raise ValueError('txcomment must by either post or comment')
        return obj_cls.as_unique(session, **prepared)

    @classmethod
    def _prepare_for_storage(cls, **kwargs):
        data_dict = kwargs['data_dict']
        try:
            prepared = {k: v(data_dict) for k, v in cls._fields.items()}
            return prepared
        except Exception as e:
            extra = dict(_fields=cls._fields, error=e, **kwargs)
            logger.exception(e, extra=extra)
            return None

    __mapper_args__ = {'polymorphic_on': type}

    @property
    def bto(self):
        return self.block_num, self.transaction_num, self.operation_num

    def __repr__(self):
        return "<%s (id=%s bto=%s author=%s title=%s)>" % (
            self.__class__.__name__, self.id, self.bto, self.author_name,
            self.title)

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
    def find_missing(cls, session):
        from .tx import TxComment
        return session.query(TxComment).outerjoin(
            cls,
            and_(TxComment.block_num == cls.block_num,
                 TxComment.transaction_num == cls.transaction_num,
                 TxComment.operation_num == cls.operation_num)).filter(
                     cls.block_num.is_(None)).order_by(TxComment.block_num)

    @classmethod
    def find_missing_block_nums(cls, session):
        from .tx import TxComment
        q = session.query(TxComment.block_num).outerjoin(
            cls,
            and_(TxComment.block_num == cls.block_num,
                 TxComment.transaction_num == cls.transaction_num,
                 TxComment.operation_num == cls.operation_num)).filter(
                     cls.block_num.is_(None)).order_by(TxComment.block_num)
        block_nums = [r[0] for r in q.all()]
        return block_nums

    @classmethod
    def add_missing(cls, sessionmaker):
        session = sessionmaker()
        missing = cls.find_missing(session)
        cls.add_txs(missing.yield_per(100), sessionmaker)

    @classmethod
    def add_txs(cls, items, sessionmaker):
        session = sessionmaker()
        for tx in items:
            if tx.is_comment:
                obj_cls = Comment
                cls_name = 'Comment'
            elif tx.is_post:
                obj_cls = Post
                cls_name = 'Post'
            else:
                raise ValueError('txcomment must by either post or comment')
            prepared = cls.prepare_from_tx(tx, session=session)
            logger.debug('%s.add: tx: %s prepared:%s', cls_name, tx, prepared)
            if not prepared:
                logger.warning('skipping prepared with no value from tx: %s',
                               tx)
                continue
            new_obj = obj_cls(**prepared)
            try:
                session.add(new_obj)
                session.commit()
            # pylint: disable=broad-except
            except Exception as e:
                session.rollback()
                logger.warning('%s.add fail: %s', cls_name, new_obj)
                logger.exception(e)
            else:
                logger.info('%s.add success: %s', cls_name, new_obj)

    @classmethod
    def merge_txs(cls, items, sessionmaker):
        session = sessionmaker()
        for tx in items:
            if tx.is_comment:
                obj_cls = Comment
                cls_name = 'Comment'
            elif tx.is_post:
                obj_cls = Post
                cls_name = 'Post'
            else:
                raise ValueError('txcomment must by either post or comment')
            prepared = cls.prepare_from_tx(tx, session=session)
            logger.debug('%s.merge: tx: %s prepared:%s', cls_name, tx,
                         prepared)
            new_obj = obj_cls(**prepared)
            try:
                session.merge(new_obj)
                session.commit()
            # pylint: disable=broad-except
            except Exception as e:
                session.rollback()
                logger.error('%s.merge fail: %s', cls_name, new_obj)
                logger.exception(e)
            else:
                logger.debug('%s.merge success: %s', cls_name, new_obj)


class Post(PostAndComment):
    author = relationship('Account', backref='posts')
    tags = relationship("Tag", secondary='sbds_syn_tag_table', backref='posts')

    __mapper_args__ = {'polymorphic_identity': 'post'}


class Comment(PostAndComment):
    author = relationship('Account', backref='comments')
    tags = relationship(
        "Tag", secondary='sbds_syn_tag_table', backref='comments')

    __mapper_args__ = {'polymorphic_identity': 'comment'}


class Tag(Base, SynthBase):
    __tablename__ = 'sbds_syn_tags'

    _id = Column(Unicode(50), primary_key=True)

    @hybrid_property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_string):
        self._id = self.format_id_string(id_string)

    @classmethod
    def format_id_string(cls, id_string):
        formatted_string = id_string.strip().lower()
        if id_string != formatted_string:
            logger.debug('tag string formatted to %s from %s',
                         formatted_string, id_string)
        return formatted_string

    # pylint: disable=unused-argument
    @classmethod
    def unique_hash(cls, *args, **kwargs):
        return cls.format_id_string(kwargs['id'])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        id_string = cls.format_id_string(kwargs['id'])
        return query.filter(cls.id == id_string)

    # pylint: enable=unused-argument


class Link(Base, SynthBase):
    __tablename__ = 'sbds_syn_links'

    id = Column(Integer, primary_key=True)
    _url = Column(Unicode(250), index=True)
    pac_id = Column(Integer, ForeignKey(PostAndComment.id))
    extraction_source = Column(extraction_source_enum, nullable=False)
    body_offset = Column(Integer)

    post_and_comment = relationship('PostAndComment', backref='links')

    @hybrid_property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        canonical_url = canonicalize_url(url)
        if url and not canonical_url:
            logger.error('bad url: %s', url)
        else:
            self._url = canonical_url

    # pylint: disable=unused-argument
    @classmethod
    def unique_hash(cls, *args, **kwargs):
        url = canonicalize_url(kwargs['url'])
        pac_id = kwargs.get('pac_id')
        return tuple([pac_id, url])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        url = kwargs['url']
        pac_id = kwargs.get('pac_id')
        return query.filter_by(pac_id=pac_id, url=url)

    # pylint: enable=unused-argument


class Image(Base, SynthBase):
    __tablename__ = 'sbds_syn_images'

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
        if url and not canonical_url:
            raise ValueError('bad url %s', url)
        else:
            self._url = canonical_url

    # pylint: disable=unused-argument
    @classmethod
    def unique_hash(cls, *args, **kwargs):
        url = canonicalize_url(kwargs['url'])
        pac_id = kwargs.get('pac_id')
        return tuple([pac_id, url])

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        url = kwargs['url']
        pac_id = kwargs.get('pac_id')
        return query.filter_by(pac_id=pac_id, url=url)

    # pylint: enable=unused-argument


tag_table = Table(
    'sbds_syn_tag_table',
    Base.metadata,
    Column(
        'post_and_comment_id',
        Integer,
        ForeignKey(PostAndComment.id),
        nullable=False),
    Column('tag_id', Unicode(50), ForeignKey(Tag.id), nullable=False),
    mysql_charset='utf8mb4',
    mysql_engine='innodb',
    mysql_collate='utf8mb4_general_ci')
