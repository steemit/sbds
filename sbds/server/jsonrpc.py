# -*- coding: utf-8 -*-
import bottle
from bottle import request
import funcy

from .input_parsers import parse_params

jsonrpc_error_code_map = {
    'parse_error': {
        'code': -32700,
        'message': 'Parse error'
    },
    'invalid_request': {
        'code': -32600,
        'message': 'Invalid Request'
    },
    'method_not_found': {
        'code': -32601,
        'message': 'Method not found'
    },
    'invalid_params': {
        'code': -32602,
        'message': 'Invalid params'
    },
    'internal_error': {
        'code': -32603,
        'message': 'Internal error'
    },
}


def generate_json_rpc_error(code, data=None):
    error_dict = dict(jsonrpc_error_code_map[code])
    if data:
        error_dict.update(data=data)
    return error_dict


def error(code, req_id, data=None):
    json_rpc_error = generate_json_rpc_error(code, data=data)
    json_rpc_error_dict = {
        'jsonrpc': '2.0',
        'id': req_id,
        'error': json_rpc_error
    }
    return json_rpc_error_dict


class JSONRPC(object):

    def __init__(self, path, app, logger):
        self.path = path
        self.app = app
        self.methods = {}
        self.logger = logger
        self.make_endpoint()

    # pylint: disable=unused-variable, too-many-return-statements,unsubscriptable-object,assignment-from-none
    def make_endpoint(self):
        @funcy.log_calls(self.logger.debug, errors=True)
        @self.app.post(self.path)
        def rpc(db):
            # parse json-rpc request envelope and params
            try:

                json_rpc_request = request.json
                json_rpc_version = json_rpc_request['jsonrpc']
                assert json_rpc_version == '2.0'
                json_rpc_method = json_rpc_request['method']
                json_rpc_id = json_rpc_request['id']
            except KeyError as e:
                data = 'Bad or missing json-rpc field %s' % e
                return error('invalid_request',
                             json_rpc_request.get('id', 'missing'), data)
            except AssertionError:
                return error(
                    'invalid_request',
                    json_rpc_request.get('id', 'missing'),
                    data='jsonrpc version must equal "2.0"')
            # unanticipated errors should be logged with more detail
            except Exception as e:
                self.logger.exception(e)
                return error('internal_error',
                             json_rpc_request.get('id', 'missing'))

            # parse json-rpc params
            try:
                # pylint: disable=no-member
                params = parse_params(json_rpc_request.get('params', None))
            except ValueError as e:
                data = 'Bad or missing json-rpc param %s' % e
                return error('invalid_params', json_rpc_id, data)
            # unanticipated errors should be logged with more detail
            except Exception as e:
                self.logger.exception(e)
                return error('internal_error', json_rpc_id)

            # lookup json-rpc method
            try:
                func = self.methods[json_rpc_method]
            except KeyError as e:
                data = 'Bad json-rpc method %s' % e
                return error('method_not_found', json_rpc_id, data)
            except Exception as e:
                self.logger.exception(e)
                return error('internal_error', json_rpc_id)

            # execute json-rpc method
            try:
                result = func(db, bottle, self.app, params)
                return {'jsonrpc': '2.0', 'id': json_rpc_id, 'result': result}
            except Exception as e:
                self.logger.exception(e)
                return error('internal_error', json_rpc_id)

    def register_method(self, method=None, name=None):
        name = name or method.__name__
        self.methods[name] = method
        self.logger.debug('registered methods: %s', self.methods.keys())

    def __call__(self, func):
        self.methods[func.__name__] = func
        self.logger.debug('registered methods: %s', self.methods.keys())


# pylint: disable=invalid-name
register_endpoint = JSONRPC
