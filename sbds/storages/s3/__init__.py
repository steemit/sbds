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

    def get(self, key):
        return loads(self.s3.Object(self.bucket, key).get()['Body'].read())

    def put(self, key, value, ignore_existing=True):
        result = self.s3.Object(self.bucket, key).put(
            Body=dumps(value).encode(), ContentEncoding='UTF-8', ContentType='application/json')

    def __contains__(self, key):
        return self.s3.Object(self.bucket, key).get()

    def __iter__(self):
        for obj in self.bucket.objects.all():
            yield loads(obj.get()['Body'].read())

    def __blocknum_dirs(self):
        paginator = self.client.get_paginator('list_objects')
        result = paginator.paginate(Bucket=self._bucket_name, Delimiter='/')
        for prefix in result.search('CommonPrefixes'):
            yield prefix.get('Prefix')

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
