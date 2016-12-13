# -*- coding: utf-8 -*-
import json
import sys
import datetime

import boto3
import click

s3_resource = boto3.resource('s3')
client = boto3.client('s3')



@click.group(name='s3')
def s3():
    '''This command provides AWS S3 steem block storage.
    It offers several subcommands.


    '''

@s3.command('create-bucket')
@click.argument('bucket', type=str)
@click.option('--region',
                help='AWS region',
                default='us-east-1')
def create_bucket(bucket, region):
    s3.create_bucket(Bucket=bucket,
                     CreateBucketConfiguration={'LocationConstraint': region})


def put_json_block(block, bucket):
    blocknum = str(block['block_num'])
    key = '/'.join(['blocknum',blocknum,'block.json'])
    data = bytes(json.dumps(block),'utf8')
    result = s3_resource.Object(bucket, key).put(Body=data,
                               ContentEncoding='UTF-8',
                               ContentType='application/json')
    return block, bucket, blocknum, key, result

@s3.command(name='put-json-blocks')
@click.argument('bucket', type=str)
@click.argument('blocks', type=click.File('r'))
def put_json_blocks(blocks, bucket):
    start = datetime.datetime.now()
    start_str = start.isoformat()
    elapsed = None
    logdata={
        'blocks': {
            'attempt': {
                'count': 0,
                'last': {
                    'blocknum': None,
                    'time': None
                }
            },
            'success' : {
                'count': 0,
                'last': {
                    'blocknum': None,
                    'time': None
                }
            },
            'fail' : {
                'count': 0,
                'last': {
                    'blocknum': None,
                    'time': None
                }
            }

        },
        'last': {
            'blocknum': None,
            'result': None
        },
        'start': start_str,
        'elapsed': 0
    }
    for block in blocks:
        now = datetime.datetime.now()
        now_str = now.isoformat()
        logdata['blocks']['attempt']['count'] += 1
        logdata['blocks']['attempt']['last']['time'] = now_str
        elapsed = now - start
        logdata['elapsed']=str(elapsed)
        try:
            block = json.loads(block)
            res_block, res_bucket, res_blocknum, res_key, s3_result = put_json_block(block, bucket)
            logdata['blocks']['attempt']['last']['blocknum'] = res_blocknum
            logdata['blocks']['attempt']['last']['key'] = res_key
            logdata['blocks']['success']['count'] += 1
            logdata['blocks']['success']['last']['blocknum'] = res_blocknum
            logdata['blocks']['success']['last']['time'] = now_str
            logdata['blocks']['success']['last']['key'] = res_key
            logdata['last']['blocknum'] = res_blocknum
            logdata['last']['result'] = 'success'
            logdata['last']['key'] = res_key
        except Exception as e:
            logdata['blocks']['fail']['count'] += 1
            logdata['blocks']['fail']['last']['blocknum'] = res_blocknum
            logdata['blocks']['fail']['last']['time'] = now_str
            logdata['last']['blocknum'] = None
            logdata['last']['result'] = 'fail'
            print('Error {} with block {}'.format(e, block), file=sys.stdout, flush=True)
        print(json.dumps(logdata, indent=2), file=sys.stderr, flush=True)



def get_top_level_keys(bucket):
    paginator = client.get_paginator('list_objects_v2')
    result = paginator.paginate(Bucket=bucket, Delimiter='/', Prefix='blocknum')




def get_missing_blockhashs():
    pass


