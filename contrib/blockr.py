#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import boto3

import click

import requests
Session = requests.Session()


def get_account_names(url):
    lower_bound_name  = 'a'
    limit = 1000
    accts = list()
    try:
        while True:
            resp = Session.post(url,json={'id':1,'jsonrpc':'2.0','method':'lookup_accounts','params':[lower_bound_name, limit]})
            accounts_in_resp = resp.json()['result']
            accts.extend(accounts_in_resp)
            if lower_bound_name == accounts_in_resp[-1]:
                break
            lower_bound_name = accounts_in_resp[-1]
    except Exception as e:
            print(e)
    valid_accounts = (a for a in accts if a not in ('',None))
    uniq_accounts = set(valid_accounts)
    sorted_accounts = sorted(list(uniq_accounts))
    return sorted_accounts


def put_json(s3_resource, bucket, key, data):
    json_data = json.dumps(data, ensure_ascii=False).encode()
    result = s3_resource.Object(bucket, key).put(
        Body=json_data, ContentEncoding='UTF-8', ContentType='application/json')
    return key, result


@click.group(name='blockr')
@click.argument('bucket', type=click.STRING, default='steemit-dev-sbds')
@click.pass_context
def blockr(ctx, bucket):
    """Steemd blockchain utils"""
    ctx.obj = dict(
        bucket=bucket,
        s3_resource=boto3.resource('s3'),
        s3_client=boto3.client('s3'),
        region='us-east-1')



@blockr.command(name='list-accounts')
@click.argument('steemd_url', type=click.STRING)
@click.pass_context
def list_accounts(ctx,steemd_url):
    accounts = get_account_names(steemd_url)
    click.echo(json.dumps(accounts))


@blockr.command(name='put')
@click.argument('steemd_url', type=click.STRING)
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT,default=20000000)
@click.pass_context
def put(ctx, steemd_url, start, end):
    s3_resource = ctx.obj['s3_resource']
    bucket = ctx.obj['bucket']
    for block_num in range(start, end+1):
        try:
            block_response = Session.post(steemd_url,json={'id':block_num,'jsonrpc':'2.0','method':'get_block','params':[block_num]})
            block = block_response.json()
            block_key = '/'.join([str(block_num), 'block.json'])
            _, block_result = put_json(s3_resource, bucket, block_key, block)
            click.echo(f'{block_num}: block result:{block_result}', err=True)
            ops_response = Session.post(steemd_url, json={
                'id': block_num, 'jsonrpc': '2.0', 'method': 'get_ops_in_block',
                'params': [block_num]
            })
            ops = ops_response.json()
            ops_key = '/'.join([str(block_num), 'ops.json'])
            _, ops_result = put_json(s3_resource, bucket, ops_key, ops)
            click.echo(f'{block_num}: ops result:{ops_result}', err=True)
        except Exception as e:
            click.echo(str(e),err=True)












if __name__ == '__main__':
    blockr()
