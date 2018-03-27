# -*- coding: utf-8 -*-

from abc import ABC
from abc import abstractmethod
from collections.abc import MutableMapping
from collections.abc import Mapping
from collections.abc import KeysView
from collections.abc import ItemsView
from collections.abc import ValuesView

from furl import furl


class AbstractStorage(MutableMapping):
    @abstractmethod
    def init(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key):
        raise KeyError

    @abstractmethod
    def __setitem__(self, key, value):
        raise KeyError

    @abstractmethod
    def __delitem__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        return dict(self.items()) == dict(other.items())

    @abstractmethod
    def __ne__(self, other):
        return not self.__eq__(other)

    @abstractmethod
    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def get(self, key, default=None):
        'D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.'
        try:
            return self[key]
        except KeyError:
            return default

    @abstractmethod
    def keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"
        return KeysView(self)

    @abstractmethod
    def items(self):
        "D.items() -> a set-like object providing a view on D's items"
        return ItemsView(self)

    @abstractmethod
    def values(self):
        "D.values() -> an object providing a view on D's values"
        return ValuesView(self)

    @abstractmethod
    def pop(self, key, default=None):
        raise NotImplementedError

    @abstractmethod
    def popitem(self):
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        'D.clear() -> None.  Remove all items from D.'
        try:
            while True:
                self.popitem()
        except KeyError:
            pass

    @abstractmethod
    def update(*args, **kwds):
        ''' D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
            If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
            If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
            In either case, this is followed by: for k, v in F.items(): D[k] = v
        '''
        if not args:
            raise TypeError("descriptor 'update' of 'MutableMapping' object "
                            "needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError('update expected at most 1 arguments, got %d' %
                            len(args))
        if args:
            other = args[0]
            if isinstance(other, Mapping):
                for key in other:
                    self[key] = other[key]
            elif hasattr(other, "keys"):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwds.items():
            self[key] = value

    @abstractmethod
    def setdefault(self, key, default=None):
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

    def __delitem__(self, key):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        raise NotImplementedError

    def pop(self, key, default=None):
        raise NotImplementedError

    def popitem(self):
        raise NotImplementedError

    def setdefault(self, key, default=None):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError
