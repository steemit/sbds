# -*- coding: utf-8 -*-
from contextlib import contextmanager
from collections import namedtuple

import sqlalchemy.orm.exc
import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import NullPool

import sbds.sbds_logging
import sbds.sbds_json

logger = sbds.sbds_logging.getLogger(__name__)


# pylint: disable=too-many-arguments, broad-except, protected-access
def _unique(session, cls, hashfunc, queryfunc, constructor, args, kwargs):
    cache = getattr(session, '_unique_cache', None)
    cls_name = cls.__name__
    if cache is None:
        session._unique_cache = cache = {}
        logger.debug('_unique created session cache')
    key = (cls, hashfunc(*args, **kwargs))
    if key in cache:
        logger.debug('_unique key %s found in session cache', key)
        return cache[key]
    else:
        logger.debug('_unique key %s not found in session cache', key)
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *args, **kwargs)
            logger.debug('_unique query %s', q)
            obj = q.one_or_none()
            if not obj:
                logger.debug('_unique query found no existing %s instance',
                             cls_name)
                obj = constructor(*args, **kwargs)

                # prevent race condition by using savepoint (begin_nested)
                session.begin(subtransactions=True)
                logger.debug('_unique beginning subtransaction')
                try:
                    logger.debug(
                        '_unique while in subtransaction: attempting to create %s',
                        obj)
                    session.add(obj)
                    session.commit()
                    logger.debug('_unique while in subtransaction: created %s',
                                 obj)
                except sqlalchemy.exc.IntegrityError as e:
                    logger.debug(
                        '_unique IntegrityError while creating %s instance',
                        cls_name)
                    session.rollback()
                    logger.debug(
                        '_unique while handling IntegrityError: rollback transaction'
                    )
                    q = session.query(cls)
                    q = queryfunc(q, *args, **kwargs)
                    obj = q.one()
                    logger.debug(
                        '_unique while handling IntegrityError: query found  %s',
                        obj)
                except Exception as e:
                    logger.error('_unique error creating %s instance: %s',
                                 cls_name, e)
                    raise e
                else:
                    logger.debug('_unique %s instance created', cls_name)
            else:
                logger.debug('_unique query found existing %s instance',
                             cls_name)
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
        return _unique(session, cls, cls.unique_hash, cls.unique_filter, cls,
                       arg, kw)


def is_duplicate_entry_error(error):
    if isinstance(error, sqlalchemy.orm.exc.FlushError):
        return 'conflicts with persistent instance' in str(error)
    elif isinstance(error, sqlalchemy.exc.IntegrityError):
        code, msg = error.orig.args
        msg = msg.lower()
        return all([code == 1062, "duplicate entry" in msg])


# pylint: disable=too-many-branches, too-many-statements
@contextmanager
def session_scope(session=None,
                  close=False,
                  expunge=False,
                  _raise_unknown=False,
                  _raise_known=False,
                  _raise_all=False):
    """Provide a transactional scope around a series of db operations."""
    if _raise_all:
        _raise_known = True
        _raise_unknown = True

    # rollback passed session if required
    if not session.is_active:
        logger.debug('rolling back passed session')
        session.rollback()
    try:
        session.info['err'] = None
        session.begin(subtransactions=True)
        yield session
        session.commit()
        session.commit()
    except (sqlalchemy.exc.IntegrityError, sqlalchemy.orm.exc.FlushError) as e:
        session.rollback()
        session.info['err'] = e
        if is_duplicate_entry_error(e):
            logger.debug('duplicate entry error caught')
        else:
            logger.exception('non-duplicate IntegrityError, unable to commit')
        if _raise_known:
            raise e
    except sqlalchemy.exc.DBAPIError as e:
        session.rollback()
        session.info['err'] = e
        logger.exception('Caught DBAPI error')
        if _raise_known:
            raise e
    except Exception as e:
        session.rollback()
        session.info['err'] = e
        logger.exception('unable to commit')
        if _raise_unknown:
            raise e
    finally:
        if close:
            logger.debug('calling session.close')
            session.close()
        elif expunge:
            logger.debug('calling session.expunge_all')
            session.expunge_all()
        if not session.is_active:
            logger.debug('second session.rollback required...rolling back')
            session.rollback()


def row_to_json(row):
    if getattr(row, 'to_json'):
        return row.to_json()
    else:
        return sbds.sbds_json.dumps(dict(row.items()))


EngineConfig = namedtuple('EngineConfig',
                          ['database_url', 'url', 'engine_kwargs', 'engine'])


def configure_engine(database_url, **kwargs):
    if kwargs:
        base_engine_kwargs = kwargs
    else:
        base_engine_kwargs = dict()

    url = make_url(database_url)
    logger.debug('configuring engine using %s', url.__repr__())
    backend = url.get_backend_name()

    if backend == 'sqlite':
        logger.debug('configuring sqlite backend')
        engine_kwargs = base_engine_kwargs
    if backend == 'mysql':
        logger.debug('configuring mysql backend')
        if 'charset' not in url.query:
            logger.debug('adding `charset=utf8mb4` to mysql engine config')
            url.query.update(charset='utf8mb4')

        engine_kwargs = base_engine_kwargs
        engine_kwargs.update(server_side_cursors=True, encoding='utf8')
    else:
        logger.debug('configuring %s backend', backend)
        engine_kwargs = base_engine_kwargs
    logger.debug('engine_kwargs: %s', engine_kwargs)

    engine = create_engine(url, **engine_kwargs)

    # create tables for in-memory db
    if backend == 'sqlite' and url.database is None:
        from .tables import Base
        Base.metadata.create_all(bind=engine, checkfirst=True)

    return EngineConfig(database_url, url, engine_kwargs, engine)


def configure_nullpool_engine(database_url, poolclass=NullPool, **kwargs):
    if kwargs:
        kwargs.pop('poolclass', None)
    return configure_engine(database_url, poolclass=poolclass, **kwargs)


@contextmanager
def isolated_nullpool_engine(database_url, **kwargs):
    engine_config = configure_nullpool_engine(database_url, **kwargs)
    engine = engine_config.engine
    try:
        yield engine
    except Exception as e:
        logger.info(e)
    finally:
        del engine_config
        engine.dispose()
        del engine


@contextmanager
def isolated_engine(database_url, **kwargs):
    engine_config = configure_engine(database_url, **kwargs)
    engine = engine_config.engine
    try:
        yield engine
    except Exception as e:
        logger.info(e)
    finally:
        del engine_config
        engine.dispose()
        del engine


@contextmanager
def isolated_engine_config(database_url, **kwargs):
    engine_config = configure_engine(database_url, **kwargs)
    try:
        yield engine_config
    except Exception as e:
        logger.info(e)
    finally:
        engine_config.engine.dispose()
        del engine_config


def get_db_processes(database_url, **kwargs):
    with isolated_nullpool_engine(database_url, **kwargs) as engine:
        if engine.url.get_backend_name() != 'mysql':
            raise TypeError('unsupported function for %s database' %
                            engine.url.get_backend_name())
        return engine.execute('SHOW PROCESSLIST').all()


def kill_db_processes(database_url, db_name=None, db_user_name=None):
    url = make_url(database_url)
    if url.get_backend_name() == 'sqlite':
        return [], []
    processes = get_db_processes(database_url)

    all_procs = []
    killed_procs = []
    with isolated_nullpool_engine(database_url) as engine:
        for process in processes:
            logger.debug(
                'process: Id:%s User:%s db:%s Command:%s State:%s Info:%s',
                process.Id, process.User, process.db, process.Command,
                process.State, process.Info)
            all_procs.append(process)
            if process.db == db_name and process.User == db_user_name:
                if process.Info != 'SHOW PROCESSLIST':
                    logger.debug('killing process %s on db %s owned by %s',
                                 process.Id, process.db, process.User)

                    engine.execute('KILL %s' % process.Id)
                    killed_procs.append(process)
        return all_procs, killed_procs
