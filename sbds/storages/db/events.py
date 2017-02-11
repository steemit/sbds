# -*- coding: utf-8 -*-
from sqlalchemy import event
from sqlalchemy.orm.session import object_session

import sbds.logging
from sbds.storages.db.tables import Session
from sbds.storages.db.tables.synthesized import Account
from sbds.storages.db.tables.synthesized import Comment
from sbds.storages.db.tables.synthesized import Post
from sbds.storages.db.tables.synthesized import PostAndComment
from sbds.storages.db.tables.tx import TxAccountCreate
from sbds.storages.db.tables.tx import TxComment
from sbds.storages.db.tables.tx import TxVote
from .utils import session_scope

logger = sbds.logging.getLogger(__name__)


def possibly_touched_instances(session, include_classes=None,
                               include_class_names=None):
    touched = session.new | session.dirty
    if include_classes:
        touched = filter(lambda x: isinstance(x, include_classes), touched)
    if include_class_names:
        touched = filter(lambda x: x.__class__.__name__ in include_class_names,
                         touched)
    return touched


def definitely_touched_instances(session, include_classes=None):
    possibly_touched = possibly_touched_instances(session,
                                                  include_classes=include_classes)
    return [i for i in possibly_touched if session.is_modified(i)]


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@event.listens_for(Session, 'before_flush')
def receive_before_flush(session, flush_context, instances):
    """listen for the 'before_flush' event"""
    '''
    Session.new
    -----------
    Instances in Session to be created: Session.new

    Session.dirty
    -------------
    Instances in Session which have been modified, but
    may be determined to be unchanged from previous values and, therefore,
    will emit no SQL

    Session.is_modified(instance, include_collections=True, passive=True)
    ---------------------------------------------------------------------

    '''
    logger.debug('before_flush event firing')


# noinspection PyUnusedLocal
@event.listens_for(Session, 'after_flush')
def receive_after_flush(session, flush_context):
    logger.debug('after_flush event fired')
    include_classes = tuple([TxComment, TxAccountCreate])
    possible_touched = possibly_touched_instances(session,
                                                  include_classes=include_classes)
    possible_touched = list(possible_touched)
    logger.debug('possibly touched instances: %s', len(possible_touched))
    account_creates = [i for i in possible_touched if
                       isinstance(i, TxAccountCreate)]
    logger.debug('possibly touched TxAccountCreate: %s', account_creates)
    comments = [i for i in possible_touched if isinstance(i, TxComment)]
    logger.debug('possibly touched TxComment: %s', comments)

    for tx in account_creates:
        name = tx.new_account_name
        created = tx.timestamp
        logger.debug(
                'after_flush attempting to create Account(name=%s, created=%s',
                name, created)
        # noinspection PyUnusedLocal
        account = Account.as_unique(session, name=name, created=created)

    for tx in comments:
        with session_scope(session) as s:
            instance = PostAndComment.from_tx(tx, session=s)
            session.add(instance)
