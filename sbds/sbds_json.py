# -*- coding: utf-8 -*-
from functools import partial

try:
    import rapidjson as json
except ImportError:
    import json

class ToStringJSONEncoder(json.JSONEncoder):
    """This encoder handles date, time, datetime, timedelta, and anything else
    with a __str__ method"""

    # pylint: disable=method-hidden
    def default(self, o):
        # pylint: disable=bare-except
        try:
            return str(o)
        except BaseException:
            return super(ToStringJSONEncoder, self).default(o)

    # pylint: enable=method-hidden


dump = partial(json.dump, cls=ToStringJSONEncoder)
dumps = partial(json.dumps, cls=ToStringJSONEncoder)
load = json.load
loads = json.loads
