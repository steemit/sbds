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

def fetch(steemd_url, block_num, method):
        if method == 'get_block':
            jsonrpc_data = dict(id=block_num,jsonrpc='2.0',method=method,params=[block_num])
        if method == 'get_ops_in_block':
            jsonrpc_data = dict(id=block_num,jsonrpc='2.0',method=method,params=[block_num,False])
        response = Session.post(steemd_url,json=jsonrpc_data)
        response.raise_for_status()
        response_json = response.json()
        response_raw = response.content
        assert 'error' not in response_json
        assert response_json['id'] == block_num
        return response_raw, response_json

@click.group(name='blockr')
@click.option('--bucket', type=click.STRING, default='steemit-dev-sbds')
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


@blockr.command(name='put-blocks')
@click.argument('steemd_url', type=click.STRING, default='https://api.steemit.com')
@click.option('--start', type=click.INT, default=4)
@click.option('--end', type=click.INT,default=20000000)
@click.pass_context
def put_blocks(ctx, steemd_url, start, end):
    s3_resource = ctx.obj['s3_resource']
    bucket = ctx.obj['bucket']
    for block_num in range(start, end+1):
        try:
            raw, block  = fetch(steemd_url, block_num, 'get_block')
            block_key = '/'.join([str(block_num), 'block.json'])
            block = block['result']
            _, block_result = put_json(s3_resource, bucket, block_key, block)
            click.echo('{block_num}: block result:{block_result}'.format(block_num=block_num,block_result=block_result), err=True)
        except Exception as e:
            click.echo(str(e),err=True)

@blockr.command(name='put-ops')
@click.argument('steemd_url', type=click.STRING, default='https://api.steemit.com')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT,default=20000000)
@click.pass_context
def put_ops(ctx, steemd_url, start, end):
    s3_resource = ctx.obj['s3_resource']
    bucket = ctx.obj['bucket']
    for block_num in range(start, end+1):
        try:
            raw, ops = fetch(steemd_url, block_num, 'get_ops_in_block')
            ops_key = '/'.join([str(block_num), 'ops.json'])
            ops = ops['result']
            _, ops_result = put_json(s3_resource, bucket, ops_key, ops)
            click.echo('{block_num}: ops result:{ops_result}'.format(block_num=block_num,ops_result=ops_result), err=True)
        except Exception as e:
            click.echo(str(e),err=True)

@blockr.command(name='put-blocks-and-ops')
@click.argument('steemd_url', type=click.STRING, default='https://api.steemit.com')
@click.option('--start', type=click.INT, default=1)
@click.option('--end', type=click.INT,default=20000000)
@click.pass_context
def put_blocks_and_ops(ctx, steemd_url, start, end):
    s3_resource = ctx.obj['s3_resource']
    bucket = ctx.obj['bucket']
    for block_num in range(start, end+1):
        try:
            raw, block = fetch(steemd_url, block_num, 'get_block')
            block_key = '/'.join([str(block_num), 'block.json'])
            block = block['result']
            _, block_result = put_json(s3_resource, bucket, block_key, block)
            click.echo('{block_num}: block result:{block_result}'.format(block_num=block_num,block_result=block_result), err=True)
            raw, ops = fetch(steemd_url, block_num, 'get_ops_in_block')
            ops_key = '/'.join([str(block_num), 'ops.json'])
            ops = ops['result']
            _, ops_result = put_json(s3_resource, bucket, ops_key, ops)
            click.echo('{block_num}: ops result:{ops_result}'.format(block_num=block_num,ops_result=ops_result), err=True)
        except Exception as e:
            click.echo(str(e),err=True)




if __name__ == '__main__':
    blockr()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
