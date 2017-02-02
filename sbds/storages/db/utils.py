# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError

import sbds.logging

logger = sbds.logging.getLogger(__name__)


def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    cls_name = cls.__name__
    if cache is None:
        session._unique_cache = cache = {}
        logger.debug('_unique created session cache')
    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        logger.debug('_unique key %s found in session cache', key)
        return cache[key]
    else:
        logger.debug('_unique key %s not found in session cache', key)
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            logger.debug('_unique query %s', q)
            obj = q.one_or_none()
            if not obj:
                logger.debug('_unique query found no existing %s instance', cls_name)
                obj = constructor(*arg, **kw)

                # prevent race condition by using savepoint (begin_nested)
                session.begin_nested()
                logger.debug('_unique beginning nested transaction')
                try:
                    logger.debug('_unique while in nested transaction: attempting to create %s', obj)
                    session.add(obj)
                    session.commit()
                    logger.debug('_unique while in nested transaction: created %s', obj)
                except IntegrityError as e:
                    logger.debug('_unique IntegrityError while creating %s instance', cls_name)
                    session.rollback()
                    logger.debug('_unique while handling IntegrityError: rollback transaction')
                    q = session.query(cls)
                    q = queryfunc(q, *arg, **kw)
                    obj = q.one()
                    logger.debug('_unique while handling IntegrityError: query found  %s', obj)
                except Exception as e:
                    logger.error('_unique error creating %s instance: %s', cls_name, e)
                    raise e
                else:
                    logger.debug('_unique %s instance created', cls_name)
            else:
                logger.debug('_unique query found existing %s instance', cls_name)
        cache[key] = obj
        return obj


class UniqueMixin(object):
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):
        return _unique(
                session,
                cls,
                cls.unique_hash,
                cls.unique_filter,
                cls,
                arg, kw
        )


def dump_tags(tree, tag):
    return tree.findall('.//%s' % tag)


def dump_images(text):
    try:
        tree = html.fromstring(text)
        imgs = dump_tags(tree, 'img') or []
        # print('lxmlimgs: %s' % imgs)
    except Exception as e:
        imgs = []
        print(e)
        print('img lxml text: %s' % text)
    try:
        tree = soupparser.fromstring(text)
        imgs2 = dump_tags(tree, 'img') or []
        # print('soupimgs: %s' % imgs2)
    except Exception as e:
        imgs2 = []
        print(e)
        print('img soup text: %s' % text)
    imgs.extend(imgs2)
    return [img.attrib.get('src') for img in imgs if img.attrib.get('src')]


def dump_links(text):
    from lxml import html
    from lxml.html import soupparser
    from markdown import markdown

    links = dict(md={'lxml': [], 'soup': []}, txt={'lxml': [], 'soup': []})
    images = dict(md={'lxml': [], 'soup': []}, txt={'lxml': [], 'soup': []})
    for i, t in enumerate((text, markdown(text), 1)):
        label = 'md'
        if i is 1:
            label = 'text'
        try:
            tree = html.fromstring(t)
            images[label]['lxml'].extend(img.attrib.get('src') for img in dump_tags(tree, 'img'))
            links[label]['lxml'].extend(link.attrib.get('href') for link in dump_tags(tree, 'a'))
        except Exception as e:
            # logger.info('lmxl %s error' % label)
            pass
        try:
            tree = soupparser.fromstring(t)
            images[label]['soup'].extend(img.attrib.get('src') for img in dump_tags(tree, 'img'))
            links[label]['soup'].extend(link.attrib.get('href') for link in dump_tags(tree, 'a'))
        except Exception as e:
            pass

    return images, links


# Testing / Dev helper funtions
def gzblocks_gen(filename):
    import gzip
    with gzip.open(filename, mode='rt', encoding='utf8') as f:
        for block in f.readlines():
            yield block


def gzblocks(filename):
    import gzip
    with gzip.open(filename, mode='rt', encoding='utf8') as f:
        return f.readlines()


def random_blocks(blocks, size=1000):
    import random
    return random.sample(blocks, size)


def create_tables(engine):
    import sbds.storages.db.tables
    sbds.storages.db.tables.Base.metadata.create_all(bind=engine)


def new_session(session=None, session_factory=None):
    session = session or session_factory()
    session.rollback()
    session.close_all()
    return session_factory()


def filter_tables(metadata, table_names):
    filtered = [t for t in metadata.sorted_tables if t.name not in table_names]
    return filtered


def reset_tables(engine, metadata, exclude_tables=None):
    exclude_tables = exclude_tables or tuple()
    for t in exclude_tables:
        if t not in [tbl.name for tbl in metadata.tables]:
            raise ValueError('excluding non-existent table %s, is this a typo?', t)
    drop_tables = filter_tables(metadata, exclude_tables)
    try:
        metadata.drop_all(bind=engine, tables=drop_tables)
    except Exception as e:
        logger.error(e)
    metadata.create_all(bind=engine)


def is_duplicate_entry_error(error):
    code, msg = error.orig.args
    msg = msg.lower()
    return all([code == 1062, "duplicate entry" in msg, "for key 'primary'" in msg])
