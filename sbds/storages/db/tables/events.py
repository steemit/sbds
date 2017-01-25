# -*- coding: utf-8 -*-
from sqlalchemy import event
from sqlalchemy import inspect

import sbds.logging
from sbds.storages.db.tables import Session

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

    #