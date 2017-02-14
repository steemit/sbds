# -*- coding: utf-8 -*-
import json
from functools import partial


class ToStringJSONEncoder(json.JSONEncoder):
    """This encoder handles date, time, datetime, timedelta, and anything else
    with a __str__ method"""
    def default(self, obj):
        # pylint: disable=bare-except
        try:
            return str(obj)
        except:
            return super(ToStringJSONEncoder, self).default(obj)

dump = partial(json.dump,  cls=ToStringJSONEncoder)
dumps = partial(json.dumps,  cls=ToStringJSONEncoder)