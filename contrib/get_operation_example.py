#!/usr/bin/env python

# coding=utf-8
import json
import subprocess

import click
import inflect

p = inflect.engine()

BAD_MYSQLSH_OUTPUT = '''{\n    "info": "mysqlx: [Warning] Using a password on the command line interface can be insecure."\n}\n'''

OLD_TABLE_NAME_MAP = {
    'delegate_vesting_shares_operation': 'sbds_tx_delegate_vesting_shares',
    'decline_voting_rights_operation': 'sbds_tx_decline_voting_rights',
    'cancel_transfer_from_savings_operation': 'sbds_tx_cancel_transfer_from_savings',
    'transfer_from_savings_operation': 'sbds_tx_transfer_from_savings',
    'transfer_to_savings_operation': 'sbds_tx_transfer_to_savings',
    'set_withdraw_vesting_route_operation': 'sbds_tx_withdraw_vesting_routes',
    'comment_options_operation': 'sbds_tx_comments_options'
}

def op_old_table_name(op_name):
    print(op_name)
    table_name = OLD_TABLE_NAME_MAP.get(op_name)
    if not table_name:
        short_op_name = op_name.replace('_operation','')
        table_name =  f'sbds_tx_{INFLECTOR.plural(short_op_name)}'
    else:
        print(table_name)

    return table_name

def get_op_example(op_name, db_url, table_name=None):
    if not table_name:
        table_name = op_old_table_name(op_name)
    op_block_query = f'SELECT {table_name}.block_num, transaction_num, operation_num, raw FROM {table_name} JOIN sbds_core_blocks ON {table_name}.block_num=sbds_core_blocks.block_num LIMIT 1;'
    proc_result = subprocess.run([
        'mysqlsh',
        '--json',
        '--uri', db_url,
        '--sqlc'],
        input=op_block_query.encode(),
        stdout=subprocess.PIPE)
    try:
        output = proc_result.stdout.decode().replace(BAD_MYSQLSH_OUTPUT,'')
        result_json = json.loads(output)
        transaction_num = result_json['rows'][0]['transaction_num']
        operation_num = result_json['rows'][0]['operation_num']
        block = json.loads(result_json['rows'][0]['raw'])
        example = block['transactions'][transaction_num -1]['operations'][operation_num -1][1]
        if example:
            return json.dumps(example, indent=2)
        return example
    except Exception as e:
        return ''

def read_json_file(ctx, param, f):
    return json.load(f)


@click.command()
@click.argument('operation_name', type=click.STRING)
@click.argument('database_url', type=click.STRING)
def cli(operation_name, database_url):
    op_example = get_op_example(operation_name, database_url)
    print(op_example)


if __name__ == '__main__':
    cli()
