# -*- coding: utf-8 -*-
from sqlalchemy import event
from sqlalchemy import inspect
from sqlalchemy.orm.session import object_session

import sbds.logging
from sbds.storages.db.tables import Session
from sbds.storages.db.tables.transaction_classes import TxAccountCreate
from sbds.storages.db.tables.transaction_classes import TxComment
from sbds.storages.db.tables.transaction_classes import TxVote
from sbds.storages.db.tables.synthesized_classes import Comment
from sbds.storages.db.tables.synthesized_classes import Post
from sbds.storages.db.tables.synthesized_classes import Account

logger = sbds.logging.getLogger(__name__)

# standard decorator style
@event.listens_for(Session, 'before_flush')
def receive_before_flush(session, flush_context, instances):
    "listen for the 'before_flush' event"
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
    logger.debug('before_flush event fired')


def possibly_touched_instances(session, include_classes=None, include_class_names=None):
    #instances = session.new + session.dirty
    touched = []
    for instances in (session.new, session.dirty):
        if include_classes:
            touched += [i for i in instances if isinstance(i, (include_classes))]
        elif include_class_names:
            touched += [i for i in instances if i.__class__.__name__ in include_class_names]
        else:
            touched  += instances
    return touched

def definitely_touched_instances(session, include_classes=None):
    possibly_touched = possibly_touched_instances(session, include_classes=include_classes)
    return [i for i in possibly_touched if session.is_modified(i)]

@event.listens_for(Session, 'after_flush')
def receive_after_flush(session, flush_context):
    logger.debug('after_flush event fired')
    touched = possibly_touched_instances(session, include_classes=(TxAccountCreate))
    logger.debug('after_flush found %s touched TxAccountCreate instances', len(touched))

    for t in touched:
        name = t.new_account_name
        created = t.transaction.block.timestamp
        logger.debug('after_flush attmepting to create Account(name=%s, created=%s', name, created)
        account = Account.as_unique(session, name=name, created=created)


event.listens_for(Comment, 'before_insert')
def receive_before_insert(mapper, connection, target):
    # set parent_id correctly
    pass

@event.listens_for(TxVote, 'after_insert')
def receive_after_insert(mapper, connection, target):
    # update author vote counts
    # update post/comment vote counts
    pass


@event.listens_for(TxComment, 'after_insert')
def receive_after_insert(mapper, connection, target):
    # create Post or Comment
    logger.debug('TxComment after_insert event fired')
    session = object_session(target)

    if target.is_comment:
        new_obj = Comment.from_tx(target)
        cls_name = 'Comment'

    elif target.is_post:
        new_obj = Post.from_tx(target)
        cls_name = 'Post'
    else:
        extra = dict(target=target)
        logger.warn('Did not create Post or Comment from TxComment', extra)
        return
    try:
        session.begin(subtransactions=True)
        author_name = target.author
        account = Account.as_unique(session,
                                    name=author_name,
                                    created=target.transaction.block.timestamp)
        new_obj.author = account
        session.add(new_obj)
        session.commit()
    except Exception as e:
        extra = dict(target=target, error=e, new_obj=new_obj)
        logger.error('Failed to add %s', cls_name, extra=extra)
        session.rollback()
        return
    else:
        logger.debug('Created %s', cls_name)


@event.listens_for(TxAccountCreate, 'after_insert')
def receive_after_insert(mapper, connection, target):
    "listen for the 'after_insert' event"
    return
    logger.debug('TxAccountCreate after_insert event fired')
    session = Session()
    #session = object_session(target)

    # create Account
    new_obj = Account.as_unique(session=session,
                                name=target.new_account_name,
                                created=target.transaction.block.timestamp)
    try:
        session.add(new_obj)
        session.commit()

    except Exception as e:
        extra = dict(target=target, error=e, new_obj=new_obj )
        logger.error('TxAccountCreate after insert failed to add Account', extra=extra)
        session.rollback()
    else:
        logger.debug('TxAccountCreate after insert created an Account')