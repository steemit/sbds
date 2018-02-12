# -*- coding: utf-8 -*-
from itertools import chain
from itertools import starmap
from itertools import tee

import maya
'''
24h 7d 30d with two trailing periods
'''
STANDARD_WINDOWS_ARGS = (
    (24, 'hours', 3),
    (7, 'days', 3),
    (30, 'days', 3), )
STANDARD_WINDOW_LABELS = ('past_24_hours', 'past_24_to_48_hours',
                          'past_48_to_72_hours', 'past_7_days',
                          'past_7_to_14_days', 'past_14_to_21_days',
                          'past_30_days', 'past_30_to_60_days',
                          'past_60_to_90_days')


def trailing_periods(step, units, periods):
    """

    Args:
        step (int):
        units (str):
        periods (int):

    Yields:
        datetime.datetime
    """
    for count in range(0, (step * periods) + 1, step):
        when = '{count} {units} ago'.format(count=count, units=units)
        yield maya.when(when).datetime(naive=True)


def trailing_windows(window_size=24, window_units='hours', window_count=3):
    """

    Args:
        window_size (int):
        window_units (str):
        window_count (int):

    Yields:
        Dict[str,str]

    """
    tos, froms = tee(trailing_periods(window_size, window_units, window_count))
    next(froms, None)
    for to, _from in zip(tos, froms):
        yield {'_from': _from, 'to': to}


def standard_trailing_windows():
    return chain.from_iterable(
        starmap(trailing_windows, STANDARD_WINDOWS_ARGS))

# pylint: disable=too-many-locals
def blockchain_stats_query(session):
    import operator as op
    from .tables.operations import AccountCreateOperation
    from .tables.operations import AccountCreateWithDelegationOperation
    from .tables.operations import CommentOperation
    from .tables.operations import VoteOperation
    from .tables.operations import TransferOperation

    account_creates = AccountCreateOperation.standard_windowed_count(session)
    account_creates_with_delegation = AccountCreateWithDelegationOperation.standard_windowed_count(
        session)
    combined_account_creates = map(op.add, account_creates,
                                   account_creates_with_delegation)

    votes = VoteOperation.standard_windowed_count(session)
    payments = TransferOperation.standard_windowed_count(session)
    post_count_query = CommentOperation.post_count_query(session)
    windowed_post_queries = CommentOperation.standard_trailing_windowed_queries(
        post_count_query)

    comment_count_query = CommentOperation.comment_count_query(session)
    windowed_comment_queries = CommentOperation.standard_trailing_windowed_queries(
        comment_count_query)

    post_counts = tuple(query.scalar() for query in windowed_post_queries)
    comment_counts = tuple(query.scalar()
                           for query in windowed_comment_queries)
    return dict(
        labels=STANDARD_WINDOW_LABELS,
        account_creates=tuple(combined_account_creates),
        votes=tuple(votes),
        payments=tuple(payments),
        post_counts=post_counts,
        comment_counts=comment_counts)
