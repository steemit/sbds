# -*- coding: utf-8 -*-
from datetime import datetime
from functools import singledispatch
from functools import partial

import rapidjson as json


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


# noinspection PyUnresolvedReferences
@to_serializable.register(datetime)
def ts_datetime(val):
    """Used if *val* is an instance of datetime."""
    return val.isoformat()


dump = partial(json.dump, default=to_serializable, ensure_ascii=True)
dumps = partial(json.dumps, default=to_serializable, ensure_ascii=True)
load = json.load
loads = json.loads
