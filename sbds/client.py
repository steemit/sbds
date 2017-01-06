# coding=utf-8
import concurrent.futures
import json
from collections import defaultdict
import math

import requests

import sbds.logging

logger = sbds.logging.getLogger(__name__)

""" Error Classes """


class UnauthorizedError(Exception):
    pass


class RPCError(Exception):
    pass


class RPCConnection(Exception):
    pass


""" API class """


class SimpleSteemAPIClient(object):
    """ Simple Steem JSON-HTTP-RPC API

        This class serves as an abstraction layer for easy use of the
        Steem API.

        :param str url: url of the API server

        All RPC commands of the Simple Steem client are exposed as methods
        in the class ``grapheneapi``. Once an instance of Simple SteemAPI is
        created with host, port, username, and password, e.g.,

        .. code-block:: python

            from sbds.client import SimpleSteemAPIClient
            rpc = SimpleSteemAPIClient("http://domain.com:port")

        any call available to that port can be issued using the instance
        via the syntax rpc.*command*(*parameters*). Example:

        .. code-block:: python

            rpc.info()

        .. note:: A distinction has to be made whether the connection is
                  made to a **witness/full node** which handles the
                  blockchain and P2P network, or a **cli-wallet** that
                  handles wallet related actions! The available commands
                  differ drastically!

        Again, the witness node does not offer access to construct any transactions,
        and hence the calls available to the witness-rpc can be seen as read-only for
        the blockchain.
    """

    def __init__(self, urls=None, **kwargs):
        self.fallback_urls = ['http://steemd-dev5.us-east-1.elasticbeanstalk.com:80',
                              'http://this.piston.rocks', 'http://steemit.com/wspa']
        self.urls = self.fallback_urls
        if isinstance(urls, (list, tuple)):
            self.urls += urls
        elif isinstance(urls, str):
            self.urls.append(urls)

        self.mode = kwargs.get('mode', 'single')

        self.headers = {'content-type': 'application/json'}
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')


    def test_urls(self, attempts=10):
        payload = json.dumps(
                {
                    "method": 'get_dynamic_global_properties',
                    "params": [],
                    "jsonrpc": "2.0",
                    "id": 0
                })

        results = defaultdict(list)
        for url in self.urls:
            fails = 0
            for i in range(attempts):
                try:
                    response = requests.post(url, data=payload, headers=self.headers, timeout=1)
                    if response.status_code == 200:
                        results[url].append(response.elapsed.total_seconds())
                    else:
                        logger.info('url:{} HTTP status fail: {}'.format(url, response.status_code))
                except Exception as e:
                    logger.info(e)

                    fails += 1
                    if fails > 3:
                        del results[url]
                        logger.info('url:{} reached fail limit: {}'.format(url, fails))
                        break
        return results

    def process_test_url_results(self, results):
        min_time = 10
        min_url = ''
        for url, seconds in results.items():
            p = percentile(seconds, percent=0.9)
            logger.info('url:{} percentile:{}'.format(url, p))
            if p < min_time:
                min_time = p
                min_url = url
        return min_time, min_url


    def tune_urls(self):
        results = self.test_urls()
        min_time, min_url = self.process_test_url_results(results)
        logger.info('min_time:{} min_url:{}'.format(min_time, min_url))
        self.urls = [min_url]


    def rpc_exec(self, url, payload, *args):
        """ Manual execute a command on API (internally used)

            param str payload: The payload containing the request
            return: Servers answer to the query
            rtype: json
            raises RPCConnection: if no connection can be made
            raises UnauthorizedError: if the user is not authorized
            raise ValueError: if the API returns a non-JSON formatted answer

            It is not recommended to use this method directly, unless
            you know what you are doing. All calls available to the API
            will be wrapped to methods directly::

                info -> grapheneapi.info()
        """
        try:
            logger.info('rpcrequest to {}'.format(url), extra=dict(appinfo=dict(payload=payload, args=args)))
            response = requests.post(url,
                                     data=json.dumps(payload, ensure_ascii=False).encode('utf8'),
                                     headers=self.headers,
                                     auth=(self.username, self.password))
            logger.info(dict(appinfo=response))
            if response.status_code == 401:
                raise UnauthorizedError
            ret = response.json()
            if 'error' in ret:
                if 'detail' in ret['error']:
                    raise RPCError(ret['error']['detail'])
                else:
                    raise RPCError(ret['error']['message'])
        except requests.exceptions.RequestException:
            raise RPCConnection("Error connecting to Client!")
        except UnauthorizedError:
            raise UnauthorizedError("Invalid login credentials!")
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")
        except RPCError as err:
            raise err
        # if isinstance(ret["result"], list) and len(ret["result"]) == 1:
        #            return ret["result"][0]
        else:
            return ret["result"]





    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments
        """
        if self.mode == 'multi':
            def method(*args):
                query = {
                    "method": name,
                    "params": args,
                    "jsonrpc": "2.0",
                    "id": 0
                }
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(self.rpc_exec, u, query) for u in self.urls]
                    r = concurrent.futures.wait(futures,
                                                return_when=concurrent.futures.FIRST_COMPLETED)
                    return r.done.pop().result()
        else:
            def method(*args):
                query = {
                    "method": name,
                    "params": args,
                    "jsonrpc": "2.0",
                    "id": 0
                }
                for url in self.fallback_urls:
                    response = self.rpc_exec(url, query)
                    if isinstance(response, dict):
                        return response
                return None
        return method

    def head_block_height(self):
        return self.get_dynamic_global_properties()['head_block_number']

    def last_irreversible_block_num(self):
        return self.get_dynamic_global_properties()['last_irreversible_block_num']



def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1