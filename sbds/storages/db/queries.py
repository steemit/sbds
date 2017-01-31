# -*- coding: utf-8 -*-
import maya

from sqlalchemy.sql import func

import sbds.logging

from ..db import Session

from .tables import Block
from .tables import Account
from .tables import PostAndComment
from .tables import Post
from .tables import Comment
from .tables import Link
from .tables import Image
from .tables import Tag

from .tables import TxAccountCreate
from .tables import TxVote

logger = sbds.logging.getLogger(__name__)

session = Session()

'''
counts
votes
article posts
comment post
signups
transactions
transfers
'''


def hours_ago(hours):
    return maya.when('%s hours ago' % hours).datetime(naive=True)


def past_24_hours():
    return maya.when('yesterday').datetime(naive=True)


def past_48_hours():
    return maya.when('day before yesterday').datetime(naive=True)


def past_72_hours():
    return maya.when('72 hours ago').datetime(naive=True)

# Counts

# votes
# account_creates
# transfers
# posts
# comments
