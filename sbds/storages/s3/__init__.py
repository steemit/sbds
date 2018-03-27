# -*- coding: utf-8 -*-
import hashlib
import itertools as it
import os
import pathlib

from functools import reduce
import boto3

import structlog


from ..base import BaseStorage
from ...sbds_json import dumps
from ...sbds_json import loads


def key(block_num, name):
    return '/'.join([str(block_num), name])


class S3Storage(BaseStorage):
    def __init__(self, uri=None, region=None):
        super().__init__(uri=uri)
        self.region = region or 'us-east-1'
        self.client = boto3.client('s3')
        self.s3 = boto3.resource('s3')
        self._bucket = self.s3.Bucket(self.uri.host)
        self._bucket_name = self.uri.host

    @property
    def bucket(self):
        return self._bucket

    def init(self):
        self.client.create_bucket(
            Bucket=self.bucket,
            CreateBucketConfiguration={'LocationConstraint': self.region})

    def test(self):
        raise NotImplementedError

    def __getitem__(self, key):
        return loads(self.s3.Object(self.bucket, key).get()['Body'].read())

    def __setitem__(self, key, value):
        result = self.s3.Object(self.bucket, key).put(
            Body=dumps(value).encode(), ContentEncoding='UTF-8', ContentType='application/json')

    def __contains__(self, key):
        return self.s3.Object(self.bucket, key).get()

    def __iter__(self):
        for obj in self.bucket.objects.all():
            yield loads(obj.get()['Body'].read())

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
        raise NotImplementedError

    def items(self):
        "D.items() -> a set-like object providing a view on D's items"
        raise NotImplementedError

    def values(self):
        "D.values() -> an object providing a view on D's values"
        raise NotImplementedError

    def __blocknum_dirs(self):
        paginator = self.client.get_paginator('list_objects')
        result = paginator.paginate(Bucket=self._bucket_name, Delimiter='/')
        for prefix in result.search('CommonPrefixes'):
            yield prefix.get('Prefix')

    def clear(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def get_block(self, block_num):
        return self.get(key(block_num, name='block.json'))

    def get_ops(self, block_num):
        return self.get(key(block_num, name='ops.json'))

    def get_block_and_ops(self, block_num):
        return (self.get(key(block_num, name='block.json')),
                self.get(key(block_num, name='ops.json')))

    def put_block(self, block_num, block, skip_exising=True):
        pass

    def put_ops(self, block_num, ops, skip_exising=True):
        pass

    def put_block_and_ops(self, block_num, block, ops, skip_existing=True):
        pass
