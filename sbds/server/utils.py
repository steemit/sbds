# -*- coding: utf-8 -*-
from bottle import response
from bottle import abort

import sbds.sbds_logging

logger = sbds.sbds_logging.getLogger(__name__)


def return_query_response(result, max_results=100000):
    response.content_type = 'application/json; charset=utf8'
    result_len = len(result)
    if result_len > max_results:
        abort(403, 'Too many rows (%s)' % result_len)
    else:
        return dict(result=[row.to_dict() for row in result])
