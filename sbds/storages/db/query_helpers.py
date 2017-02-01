# -*- coding: utf-8 -*-
import maya

from sqlalchemy.sql import func

import sbds.logging


def hours_ago(hours):
    return maya.when('%s hours ago' % hours).datetime(naive=True)


def past_24_hours():
    return maya.when('yesterday').datetime(naive=True)


def past_48_hours():
    return maya.when('day before yesterday').datetime(naive=True)


def past_72_hours():
    return maya.when('72 hours ago').datetime(naive=True)

def past_24_to_48_hours():
    return past_24_hours(), past_48_hours()

def past_48_to_72_hours():
    return past_48_hours(), past_72_hours()

