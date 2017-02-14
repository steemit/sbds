# -*- coding: utf-8 -*-

import json

import boto3
import click

import sbds.logging

logger = sbds.logging.getLogger(__name__)


@click.group(name='s3')
@click.argument('bucket', type=click.STRING)
@click.pass_context
def s3(ctx, bucket):
    """Interact with an S3 storage backend"""
    ctx.obj = dict(
        bucket=bucket,
        s3_resource=boto3.resource('s3'),
        s3_client=boto3.client('s3'),
        region='us-east-1')


@s3.command('create-bucket')
@click.pass_context
def create_bucket(ctx):
    """Create S3 bucket to store blocks"""
    region = ctx.obj['region']
    bucket = ctx.obj['bucket']
    s3_client = ctx.obj['s3_client']
    s3_client.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={'LocationConstraint': region})


def put_json_block(s3_resource, block, bucket):
    blocknum = str(block['block_num'])
    key = '/'.join([blocknum, 'block.json'])
    data = bytes(json.dumps(block), 'utf8')
    result = s3_resource.Object(bucket, key).put(
        Body=data, ContentEncoding='UTF-8', ContentType='application/json')
    return block, bucket, blocknum, key, result


@s3.command(name='put-blocks')
@click.argument('blocks', type=click.File('r'))
@click.pass_context
def put_json_blocks(ctx, blocks):
    """Store JSON blocks"""
    s3_resource = ctx.obj['s3_resource']
    bucket = ctx.obj['bucket']
    for block in blocks:
        block = json.loads(block)
        # pylint: disable=unused-variable
        res_block, res_bucket, res_blocknum, res_key, s3_result = put_json_block(
            s3_resource, block, bucket)
