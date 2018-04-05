# -*- coding: utf-8 -*-

from abc import ABC
from abc import abstractmethod


from furl import furl


class AbstractStorage(ABC):

    @abstractmethod
    def init(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def test(self):
        raise NotImplementedError

    @abstractmethod
    def key(self, block_num, name):
        raise NotImplementedError

    @abstractmethod
    def get(self, key):
        raise NotImplementedError

    @abstractmethod
    def put(self, key, value, skip_existing=True):
        raise NotImplementedError

    @abstractmethod
    def get_block(self, block_num):
        raise NotImplementedError

    @abstractmethod
    def get_ops(self, block_num):
        raise NotImplementedError

    @abstractmethod
    def get_block_and_ops(self, block_num):
        raise NotImplementedError

    @abstractmethod
    def put_block(self, block_num, block, skip_existing=True):
        raise NotImplementedError

    @abstractmethod
    def put_ops(self, block_num, ops, skip_existing=True):
        raise NotImplementedError

    @abstractmethod
    def put_block_and_ops(self, block_num, block, ops, skip_existing=True):
        raise NotImplementedError


class BaseStorage(AbstractStorage):
    """

    subclasses are requred to implement:

    init
    __getitem__
    __setitem__
    __contains__
    __iter__
    __len__
    get
    keys
    items
    values

    """

    def __init__(self, uri=None):
        self.uri = furl(uri)

    @property
    def scheme(self):
        return self.uri.scheme
