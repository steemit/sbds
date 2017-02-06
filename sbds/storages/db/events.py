# -*- coding: utf-8 -*-
from sqlalchemy import event
from sqlalchemy.orm.session import object_session

import sbds.logging
from sbds.storages.db.tables import Session
from sbds.storages.db.tables.synthesized import Account
from sbds.storages.db.tables.synthesized import Comment
from sbds.storages.db.tables.synthesized import Post
from sbds.storages.db.tables.tx import TxAccountCreate
from sbds.storages.db.tables.tx import TxComment
from sbds.storages.db.tables.tx import TxVote

logger = sbds.logging.getLogger(__name__)

def possibly_touched_instances(session, include_classes=None, include_class_names=None):
    touched = session.new | session.dirty
    if include_classes:
        touched = filter(lambda x: isinstance(x, include_classes), touched)
    if include_class_names:
        touched = filter(lambda x: x.__class__.__name__ in include_class_names, touched)
    return touched


def definitely_touched_instances(session, include_classes=None):
    possibly_touched = possibly_touched_instances(session, include_classes=include_classes)
    return [i for i in possibly_touched if session.is_modified(i)]


#@event.listens_for(Session, 'before_flush')
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




#@event.listens_for(Session, 'after_flush')
def receive_after_flush(session, flush_context):
    logger.debug('after_flush event fired')
    touched = possibly_touched_instances(session, include_classes=TxAccountCreate)
    logger.debug('after_flush found %s touched TxAccountCreate instances', len(touched))

    for t in touched:
        name = t.new_account_name
        created = t.transaction.block.timestamp
        logger.debug('after_flush attempting to create Account(name=%s, created=%s', name, created)
        account = Account.as_unique(session, name=name, created=created)



@event.listens_for(TxComment, 'after_insert')
def receive_after_insert(mapper, connection, target):
    # create Post or Comment
    logger.debug('TxComment after_insert event firing')
    session = Session()
    if target.is_comment:
        new_obj = Comment.from_tx(target)
        cls_name = 'Comment'

    elif target.is_post:
        new_obj = Post.from_tx(target)
        cls_name = 'Post'
    else:
        extra = dict(target=target)
        logger.warning('Did not create Post or Comment from TxComment', extra)
        return
    try:
        session.begin(subtransactions=True)
        session.add(new_obj)
        session.commit()
    except Exception as e:
        extra = dict(target=target, error=e, new_obj=new_obj)
        logger.error('Failed to add %s', cls_name, extra=extra)
        session.rollback()
        return
    else:
        logger.debug('Created %s', cls_name)
