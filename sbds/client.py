# coding=utf-8
import concurrent.futures
import json

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
        self.fallback_urls = ['http://this.piston.rocks', 'http://34.192.222.110:80']
        self.urls = self.fallback_urls
        if isinstance(urls, (list, tuple)):
            self.urls += urls
        elif isinstance(urls, str):
            self.urls.append(urls)

        self.headers = {'content-type': 'application/json'}
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')

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
            ret = json.loads(response.text)
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

        return method

    def head_block_height(self):
        return self.get_dynamic_global_properties()['head_block_number']

    def last_irreversible_block_num(self):
        return self.get_dynamic_global_properties()['last_irreversible_block_num']
