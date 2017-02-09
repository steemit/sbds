# coding=utf-8
import os
import ujson as json
from functools import partial
from functools import partialmethod
from urllib.parse import urlparse

import urllib3

import sbds.utils

logger = sbds.logging.getLogger(__name__)


class RPCError(Exception):
    pass


class RPCConnectionError(Exception):
    pass


class SimpleSteemAPIClient(object):
    """ Simple Steem JSON-HTTP-RPC API

        This class serves as an abstraction layer for easy use of the
        Steem API.

        :param str url: url of the API server
        :param urllib3.HTTPConnectionPool url: instance of urllib3.HTTPConnectionPool

        .. code-block:: python

            from sbds.client import SimpleSteemAPIClient
            rpc = SimpleSteemAPIClient("http://domain.com:port")

        any call available to that port can be issued using the instance
        via the syntax rpc.exec_rpc('command', (*parameters*). Example:

        .. code-block:: python

            rpc.exec('info')

    """

    def __init__(self, url=None, log_level='INFO', **kwargs):
        url = url or os.environ.get('STEEMD_HTTP_URL')
        self.url = url
        self.hostname = urlparse(url).hostname
        maxsize = kwargs.get('maxsize', 20)
        timeout = kwargs.get('timeout', 10)
        pool_block = kwargs.get('pool_block', True)
        self.http = urllib3.poolmanager.PoolManager(
                num_pools=10,
                headers={'Content-Type':'application/json'},
                maxsize=maxsize,
                timeout=timeout)
        '''
        urlopen(method, url, body=None, headers=None, retries=None,
        redirect=True, assert_same_host=True, timeout=<object object>,
        pool_timeout=None, release_conn=None, chunked=False, body_pos=None,
        **response_kw)
        '''
        body = json.dumps({
            "method": 'get_dynamic_global_properties',
            "params": [],
            "jsonrpc": "2.0",
            "id": 0
        }, ensure_ascii=False).encode('utf8')

        self.request = partial(self.http.urlopen, 'POST', url,
                               retries=2, body=body)

        logger.setLevel(log_level)

    def exec(self, name, *args, return_json=True, raise_for_status=True):
        body = json.dumps({
            "method": name,
            "params": args,
            "jsonrpc": "2.0",
            "id": 0
        }, ensure_ascii=False).encode('utf8')
        extra = dict(appinfo=dict(body=body))
        logger.debug('rpc request to {}'.format, extra=extra )
        response = self.request(body=body)
        extra = dict(body=response.data)
        logger.debug('rpc response: %s' % response.status, extra=extra)
        if response.status not in tuple([*response.REDIRECT_STATUSES, 200]) and raise_for_status:
            logger.info('non 200 response:')
            raise RPCConnectionError(response)
        ret = json.loads(response.data.decode('utf-8'))
        if 'error' in ret:
            raise RPCError(ret['error'].get('detail', ret['error']['message']))
        result = ret["result"]
        if return_json:
            return result
        else:
            return json.dumps(result)

    def exec_multi(self, name, params):
        body_gen = (json.dumps({
            "method": name, "params": [i], "jsonrpc": "2.0", "id": 0
        }, ensure_ascii=False).encode('utf8') for i in params)
        for body in body_gen:
            yield json.loads(self.request(body=body).data.decode('utf-8'))['result']

    get_dynamic_global_properties = partialmethod(exec, 'get_dynamic_global_properties')
    get_block = partialmethod(exec, 'get_block')

    def last_irreversible_block_num(self):
        return self.get_dynamic_global_properties()['last_irreversible_block_num']

    def head_block_height(self):
        return self.get_dynamic_global_properties()['last_irreversible_block_num']

    def block_height(self):
        return self.get_dynamic_global_properties()['last_irreversible_block_num']
