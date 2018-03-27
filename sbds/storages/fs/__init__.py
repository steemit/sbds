# -*- coding: utf-8 -*-
import hashlib
import itertools as it
import os
import pathlib

from functools import reduce
import structlog


from ..base import BaseStorage
from ...sbds_json import dumps
from ...sbds_json import loads

CHARS = frozenset((
    '0', '1', '2', '3',
    '4', '5', '6', '7',
    '8', '9', 'a', 'b',
    'c', 'd', 'e', 'f'))


def key(block_num, name=None, base_path=None):
    block_num_sha = hashlib.sha1(bytes(block_num)).hexdigest()
    return pathlib.PosixPath(*[part for part in (base_path,
                                                 block_num_sha[:2],
                                                 block_num_sha[2:4],
                                                 block_num_sha[4:6],
                                                 str(block_num),
                                                 name) if part])


class FileSystemStorage(BaseStorage):
    def __init__(self, uri=None):
        super().__init__(uri=uri)
        assert self.uri.path.isabsolute
        #assert self.uri.path.isdir
        self._base_path = pathlib.PosixPath(str(self.uri.path))

    @property
    def base_path(self):
        return self._base_path

    def init(self):
        prefix_permutations = it.permutations(CHARS, 6)
        base_path = self.base_path
        if not base_path.exists():
            base_path.mkdir(parents=True)
        for perm in prefix_permutations:
            path = pathlib.PosixPath(
                base_path, f'{perm[0]}{perm[1]}/{perm[2]}{perm[3]}/{perm[4]}{perm[5]}')
            if not path.exists():
                path.mkdir(parents=True)

    def test(self):
        base_path = self.base_path
        return {'exists': base_path.exists(),
                'read': os.access(base_path.as_posix(), os.R_OK),
                'write': os.access(base_path.as_posix(), os.W_OK)}

    def __getitem__(self, key):
        return loads(key.read_bytes())

    def __setitem__(self, key, value):
        key.write_bytes(dumps(value).encode())

    def __contains__(self, key):
        return key.exists()

    def __iter__(self):
        for dir in self.__blocknum_dirs():
            block_pth = pathlib.Path(dir, 'block.json')
            if block_pth.exists():
                yield block_pth.read_bytes()
            ops_pth = pathlib.Path(dir, 'ops.json')
            if ops_pth.exists():
                yield ops_pth.read_bytes()

    def __len__(self):
        return reduce(lambda x, y: x + len(y), self.__blocknum_dirs(), 0)

    def get(self, key, default=None):
        'D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.'
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"

    def items(self):
        "D.items() -> a set-like object providing a view on D's items"
        pass

    def values(self):
        "D.values() -> an object providing a view on D's values"
        pass

    def __dirs(self):
        prefix_permutations = it.permutations(CHARS, 6)
        for perm in prefix_permutations:
            yield pathlib.PosixPath(self.base_path, f'{perm[0]}{perm[1]}/{perm[2]}{perm[3]}/{perm[4]}{perm[5]}')

    def __blocknum_dirs(self):
        for dir in self.__dirs():
            if dir.exists():
                yield os.listdir(dir)

    def __blocks(self):
        for dir in self.__blocknum_dirs():
            block_pth = pathlib.Path(dir, 'block.json')
            if block_pth.exists():
                yield block_pth

    def __ops(self):
        for dir in self.__blocknum_dirs():
            ops_pth = pathlib.Path(dir, 'ops.json')
            if ops_pth.exists():
                yield ops_pth

    def clear(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def get_block(self, block_num):
        return self.get(key(block_num, base_path=self.base_path, name='block.json'))

    def get_ops(self, block_num):
        return self.get(key(block_num, base_path=self.base_path, name='ops.json'))

    def get_block_and_ops(self, block_num):
        base_key = key(block_num, base_path=self.base_path)
        return (self.get(base_key.joinpath('block.json')),
                self.get(base_key.joinpath('ops.json')))
