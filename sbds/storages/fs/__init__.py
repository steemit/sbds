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
                                                 str(block_num),
                                                 name) if part])


def key2(block_num, name=None, base_path=None):
    block_num_sha = str(block_num)
    return pathlib.PosixPath(*[part for part in (base_path,
                                                 block_num_sha[:2],
                                                 block_num_sha[2:4],
                                                 str(block_num),
                                                 name) if part])


class FileSystemStorage(BaseStorage):
    def __init__(self, uri=None):
        super().__init__(uri=uri)
        assert self.uri.path.isabsolute
        self._base_path = pathlib.PosixPath(str(self.uri.path))

    def init(self):
        prefix_permutations = it.permutations(CHARS, 6)
        base_path = self.base_path
        if not base_path.exists():
            base_path.mkdir(parents=True)
        for perm in prefix_permutations:
            path = pathlib.PosixPath(
                base_path, f'{perm[0]}{perm[1]}/{perm[2]}{perm[3]}')
            if not path.exists():
                path.mkdir(parents=True)

    def test(self):
        base_path = self.base_path
        return {'exists': base_path.exists(),
                'read': os.access(base_path.as_posix(), os.R_OK),
                'write': os.access(base_path.as_posix(), os.W_OK)}

    def key(self, block_num, name):
        return key(block_num=block_num, name=name, base_path=self.base_path)

    def get(self, key):
        try:
            return loads(key.read_bytes())
        except KeyError:
            return None

    def put(self, key, value, ignore_existing=True):
        key.write_bytes(dumps(value).encode())

    def get_block(self, block_num):
        return self.get(self.key(block_num, 'block.json'))

    def get_ops(self, block_num):
        return self.get(self.key(block_num, 'ops_in_block.json'))

    def get_block_and_ops(self, block_num):
        base_key = key(block_num, base_path=self.base_path)
        return (self.get(base_key.joinpath('block.json')),
                self.get(base_key.joinpath('ops_in_block.json')))

    def put_block(self, block_num, block, skip_existing=True):
        return self.put(self.key(block_num, 'block.json'), block)

    def put_ops(self, block_num, ops, skip_existing=True):
        return self.put(self.key(block_num, 'ops_in_block.json'), ops)

    def put_block_and_ops(self, block_num, block, ops, skip_existing=True):
        return all([
            self.put_block(block_num, block),
            self.put_ops(block_num, ops)])

    @property
    def base_path(self):
        return self._base_path

    def __dirs(self):
        prefix_permutations = it.permutations(CHARS, 4)
        for perm in prefix_permutations:
            yield pathlib.PosixPath(self.base_path, f'{perm[0]}{perm[1]}/{perm[2]}{perm[3]}')

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
