# coding=utf-8
import json
import os
import logging
from functools import partial
from functools import partialmethod
from urllib.parse import urlparse

import certifi
import urllib3

import sbds.logging

logger = sbds.logging.getLogger(__name__)


class RPCError(Exception):
    pass


class RPCConnectionError(Exception):
    pass


class SimpleSteemAPIClient(object):
    """Simple Steem JSON-HTTP-RPC API

        This class serves as an abstraction layer for easy use of the
        Steem API.

    Args:
      str: url: url of the API server
      urllib3: HTTPConnectionPool url: instance of urllib3.HTTPConnectionPool

    .. code-block:: python

    from sbds.client import SimpleSteemAPIClient
    rpc = SimpleSteemAPIClient("http://domain.com:port")

    any call available to that port can be issued using the instance
    via the syntax rpc.exec_rpc('command', (*parameters*). Example:

    .. code-block:: python

    rpc.exec('info')

    Returns:

    """

    def __init__(self, url=None, log_level=logging.INFO, **kwargs):
        url = url or os.environ.get('STEEMD_HTTP_URL')
        self.url = url
        self.hostname = urlparse(url).hostname
        self.return_with_args = kwargs.get('return_with_args', False)
        self.re_raise = kwargs.get('re_raise', False)

        maxsize = kwargs.get('maxsize', 10)
        timeout = kwargs.get('timeout', 30)
        retries = kwargs.get('retries', 10)

        pool_block = kwargs.get('pool_block', False)

        self.http = urllib3.poolmanager.PoolManager(
            num_pools=50,
            headers={'Content-Type': 'application/json'},
            maxsize=maxsize,
            block=pool_block,
            timeout=timeout,
            retries=retries,
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where())
        '''
        urlopen(method, url, body=None, headers=None, retries=None,
        redirect=True, assert_same_host=True, timeout=<object object>,
        pool_timeout=None, release_conn=None, chunked=False, body_pos=None,
        **response_kw)
        '''

        body = json.dumps(
            {
                "method": 'get_dynamic_global_properties',
                "params": [],
                "jsonrpc": "2.0",
                "id": 0
            },
            ensure_ascii=False).encode('utf8')

        self.request = partial(
            self.http.urlopen, 'POST', url, retries=2, body=body)

        _logger = sbds.logging.getLogger('urllib3')

        sbds.logging.configure_existing_logger(_logger, level=log_level)

    def exec(self, name, *args, re_raise=None, return_with_args=None):

        body = json.dumps(
            {
                "method": name,
                "params": args,
                "jsonrpc": "2.0",
                "id": 0
            },
            ensure_ascii=False).encode('utf8')
        try:
            response = self.request(body=body)
        except Exception as e:
            if re_raise:
                raise e
            else:
                extra = dict(err=e, request=self.request)
                logger.info('Request error', extra=extra)
                self._return(
                    response=None,
                    args=args,
                    return_with_args=return_with_args)
        else:
            if response.status not in tuple(
                    [*response.REDIRECT_STATUSES, 200]):
                logger.info('non 200 response:%s', response.status)

            return self._return(
                response=response,
                args=args,
                return_with_args=return_with_args)

    def _return(self, response=None, args=None, return_with_args=None):
        return_with_args = return_with_args or self.return_with_args
        try:
            response_json = json.loads(response.data.decode('utf-8'))
        except Exception as e:
            extra = dict(response=response, request_args=args, err=e)
            logger.info('failed to load response', extra=extra)
        else:
            if 'error' in response_json:
                error = response_json['error']
                error_message = error.get('detail',
                                          response_json['error']['message'])
                raise RPCError(error_message)

            result = response_json["result"]
            if return_with_args:
                return result, args
            else:
                return result

    def exec_multi(self, name, params):
        body_gen = (json.dumps(
            {
                "method": name,
                "params": [i],
                "jsonrpc": "2.0",
                "id": 0
            },
            ensure_ascii=False).encode('utf8') for i in params)
        for body in body_gen:
            yield json.loads(
                self.request(body=body).data.decode('utf-8'))['result']

    get_dynamic_global_properties = partialmethod(
        exec, 'get_dynamic_global_properties')
    get_block = partialmethod(exec, 'get_block')

    def last_irreversible_block_num(self):
        return self.get_dynamic_global_properties()[
            'last_irreversible_block_num']

    def head_block_height(self):
        return self.get_dynamic_global_properties()[
            'last_irreversible_block_num']

    def block_height(self):
        return self.get_dynamic_global_properties()[
            'last_irreversible_block_num']
