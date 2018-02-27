#!/usr/bin/env python
# -*- coding: utf-8 -*-

# coding=utf-8
import json
import os.path
import subprocess
import sys
import textwrap

from pathlib import Path

import click
import inflect

from collections import defaultdict

p = inflect.engine()


def reindent(s, numSpaces):
    if s:
        s = s.splitlines()
        s = [(numSpaces * ' ') + line.lstrip() for line in s]
        s = '\n'.join(s)
    return s


def addindent(s, numSpaces):
    if s:
        s = '\n'.join([(numSpaces * ' ') + line for line in s.splitlines()])
    return s


BAD_MYSQLSH_OUTPUT = '''{\n    "info": "mysqlx: [Warning] Using a password on the command line interface can be insecure."\n}\n'''

VIRTUAL_OPS_NAMES = (
    'author_reward_operation',
    'comment_benefactor_reward_operation',
    'comment_payout_update_operation',
    'comment_reward_operation',
    'curation_reward_operation',
    'fill_convert_request_operation',
    'fill_order_operation',
    'fill_transfer_from_savings_operation',
    'fill_vesting_withdraw_operation',
    'hardfork_operation',
    'interest_operation',
    'liquidity_reward_operation',
    'producer_reward_operation',
    'return_vesting_delegation_operation',
    'shutdown_witness_operation'
)

# virtual operations
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/steem_virtual_operations.hpp
virtual_op_source_map = {
    'author_reward_operation': '''
    struct author_reward_operation : public virtual_operation {
      author_reward_operation(){}
      author_reward_operation( const account_name_type& a, const string& p, const asset& s, const asset& st, const asset& v )
         :author(a), permlink(p), sbd_payout(s), steem_payout(st), vesting_payout(v){}

      account_name_type author;
      string            permlink;
      asset             sbd_payout;
      asset             steem_payout;
      asset             vesting_payout;
   };''',
    'curation_reward_operation': '''
    struct curation_reward_operation : public virtual_operation
   {
      curation_reward_operation(){}
      curation_reward_operation( const string& c, const asset& r, const string& a, const string& p )
         :curator(c), reward(r), comment_author(a), comment_permlink(p) {}

      account_name_type curator;
      asset             reward;
      account_name_type comment_author;
      string            comment_permlink;
   };''',
    'comment_reward_operation': '''
    struct comment_reward_operation : public virtual_operation
   {
      comment_reward_operation(){}
      comment_reward_operation( const account_name_type& a, const string& pl, const asset& p )
         :author(a), permlink(pl), payout(p){}

      account_name_type author;
      string            permlink;
      asset             payout;
   };''',
    'liquidity_reward_operation': '''
    struct liquidity_reward_operation : public virtual_operation
   {
      liquidity_reward_operation( string o = string(), asset p = asset() )
      :owner(o), payout(p) {}

      account_name_type owner;
      asset             payout;
   };''',
    'interest_operation': '''
    struct interest_operation : public virtual_operation
   {
      interest_operation( const string& o = "", const asset& i = asset(0,SBD_SYMBOL) )
         :owner(o),interest(i){}

      account_name_type owner;
      asset             interest;
   };''',
    'fill_convert_request_operation': '''
    struct fill_convert_request_operation : public virtual_operation
   {
      fill_convert_request_operation(){}
      fill_convert_request_operation( const string& o, const uint32_t id, const asset& in, const asset& out )
         :owner(o), requestid(id), amount_in(in), amount_out(out) {}

      account_name_type owner;
      uint32_t          requestid = 0;
      asset             amount_in;
      asset             amount_out;
   };''',
    'fill_vesting_withdraw_operation': '''
       struct fill_vesting_withdraw_operation : public virtual_operation
   {
      fill_vesting_withdraw_operation(){}
      fill_vesting_withdraw_operation( const string& f, const string& t, const asset& w, const asset& d )
         :from_account(f), to_account(t), withdrawn(w), deposited(d) {}

      account_name_type from_account;
      account_name_type to_account;
      asset             withdrawn;
      asset             deposited;
   };''',
    'shutdown_witness_operation': '''
       struct shutdown_witness_operation : public virtual_operation
   {
      shutdown_witness_operation(){}
      shutdown_witness_operation( const string& o ):owner(o) {}

      account_name_type owner;
   };''',
    'fill_order_operation': '''
    struct fill_order_operation : public virtual_operation
   {
      fill_order_operation(){}
      fill_order_operation( const string& c_o, uint32_t c_id, const asset& c_p, const string& o_o, uint32_t o_id, const asset& o_p )
      :current_owner(c_o), current_orderid(c_id), current_pays(c_p), open_owner(o_o), open_orderid(o_id), open_pays(o_p) {}

      account_name_type current_owner;
      uint32_t          current_orderid = 0;
      asset             current_pays;
      account_name_type open_owner;
      uint32_t          open_orderid = 0;
      asset             open_pays;
   };''',
    'fill_transfer_from_savings_operation': '''
    struct fill_transfer_from_savings_operation : public virtual_operation
   {
      fill_transfer_from_savings_operation() {}
      fill_transfer_from_savings_operation( const account_name_type& f, const account_name_type& t, const asset& a, const uint32_t r, const string& m )
         :from(f), to(t), amount(a), request_id(r), memo(m) {}

      account_name_type from;
      account_name_type to;
      asset             amount;
      uint32_t          request_id = 0;
      string            memo;
   };''',
    'hardfork_operation': '''
    struct hardfork_operation : public virtual_operation
   {
      hardfork_operation() {}
      hardfork_operation( uint32_t hf_id ) : hardfork_id( hf_id ) {}

      uint32_t         hardfork_id = 0;
   };''',
    'comment_payout_update_operation': '''
    struct comment_payout_update_operation : public virtual_operation
   {
      comment_payout_update_operation() {}
      comment_payout_update_operation( const account_name_type& a, const string& p ) : author( a ), permlink( p ) {}

      account_name_type author;
      string            permlink;
   };''',
    'return_vesting_delegation_operation': '''
    struct return_vesting_delegation_operation : public virtual_operation
   {
      return_vesting_delegation_operation() {}
      return_vesting_delegation_operation( const account_name_type& a, const asset& v ) : account( a ), vesting_shares( v ) {}

      account_name_type account;
      asset             vesting_shares;
   };''',
    'comment_benefactor_reward_operation': '''
    struct comment_benefactor_reward_operation : public virtual_operation
   {
      comment_benefactor_reward_operation() {}
      comment_benefactor_reward_operation( const account_name_type& b, const account_name_type& a, const string& p, const asset& r )
         : benefactor( b ), author( a ), permlink( p ), reward( r ) {}

      account_name_type benefactor;
      account_name_type author;
      string            permlink;
      asset             reward;
   };''',
    'producer_reward_operation': '''
    struct producer_reward_operation : public virtual_operation
   {
      producer_reward_operation(){}
      producer_reward_operation( const string& p, const asset& v ) : producer( p ), vesting_shares( v ) {}

      account_name_type producer;
      asset             vesting_shares;

   };'''
}


class_template = '''\
# coding=utf-8

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean
from sqlalchemy import SmallInteger
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey

from sqlalchemy.dialects.postgresql import JSONB

from ..{op_rel_import_dot}import Base
from ...{op_rel_import_dot}enums import operation_types_enum
from ...{op_rel_import_dot}field_handlers import amount_field
from ...{op_rel_import_dot}field_handlers import amount_symbol_field
from ...{op_rel_import_dot}field_handlers import comment_body_field
from .{op_rel_import_dot}base import BaseOperation
from .{op_rel_import_dot}base import BaseVirtualOperation

class {op_class_name}(Base, {op_class_operation_base}):
    """


    Steem Blockchain Example
    ======================
{op_example}



    """

    __tablename__ = '{op_table_name}'
    __operation_type__ = '{op_name}'

{op_columns}
    operation_type = Column(
        operation_types_enum,
        nullable=False,
        index=True,
        default='{op_name}')

    _fields = dict(
{op_fields}
    )

'''

name_to_columns_map = defaultdict(lambda: [])
name_to_columns_map.update({
    'json_metadata': ['json_metadata = Column(JSONB) # name:json_metadata'],
    'from': ["_from = Column('from',String(50), ForeignKey('sbds_meta_accounts.name')) # name:from"],
    'json': ['json = Column(JSONB) # name:json'],
    'posting': ['posting = Column(JSONB) # name:posting'],
    'owner': ['owner = Column(JSONB) # name:owner'],
    'active': ['active = Column(JSONB) # name:active'],
    'body': ['body = Column(UnicodeText) # name:body'],
    'json_meta': ['json_meta = Column(JSONB) # name:json_meta'],
    'memo': ['memo = Column(UnicodeText) # name:memo'],
    'permlink': ['permlink = Column(Unicode(512), index=True) # name:permlink'],
    'parent_permlink': ['parent_permlink = Column(Unicode(512), index=True) # name:parent_permlink'],
    'title,comment_operation': ['title = Column(Unicode(512), index=True) # name:title,comment_operation'],

})


OLD_TABLE_NAME_MAP = {
    'delegate_vesting_shares_operation': 'sbds_tx_delegate_vesting_shares',
    'decline_voting_rights_operation': 'sbds_tx_decline_voting_rights',
    'cancel_transfer_from_savings_operation': 'sbds_tx_cancel_transfer_from_savings',
    'transfer_from_savings_operation': 'sbds_tx_transfer_from_savings',
    'transfer_to_savings_operation': 'sbds_tx_transfer_to_savings',
    'set_withdraw_vesting_route_operation': 'sbds_tx_withdraw_vesting_routes',
    'comment_options_operation': 'sbds_tx_comments_options'
}


SMALL_INT_TYPES = (
    'uint16_t',
    'int8_t',
    'int16_t'
)

INT_TYPES = (
    'uint32_t',
    'int32_t'
)

BIG_INT_TYPES = (
    'uint64_t',
    'int64_t',
)


def get_fields(name, _type):
    fields = []
    if _type == 'asset':
        # amount_field(x.get('amount'), num_func=float)
        fields.append(
            f"{name}=lambda x: amount_field(x.get('{name}'), num_func=float),")
        fields.append(
            f"{name}_symbol=lambda x: amount_symbol_field(x.get('{name}')),")
    elif name == 'body':
        # body = lambda x: comment_body_field(x['body']),
        fields.append(
            f"{name}=lambda x: comment_body_field(x.get('{name}')),")
    return fields


def get_columns(name, _type, op_name):
    cols = name_to_columns_map.get(f'{name},{op_name}')
    if not cols:
        cols = name_to_columns_map.get(name)
    if not cols:
        cols = _get_columns_by_type(name, _type)
    return cols


def _get_columns_by_type(name, _type):
    # asset
    if _type == 'asset':
        if name == 'from':
            return [
                f'_from = Column("from",Numeric(20,6), nullable=False) # steem_type:asset',
                f'from_symbol = Column(String(5)) # steem_type:{_type}']
        return [
            f'{name} = Column(Numeric(20,6), nullable=False) # steem_type:asset',
            f'{name}_symbol = Column(String(5)) # steem_type:{_type}']

    # account_name_type
    elif _type == 'account_name_type':
        return [f'{name} = Column(String(50), ForeignKey("sbds_meta_accounts.name")) # steem_type:{_type}']

    # public_key_type
    elif _type == 'public_key_type':
        return [f'{name} = Column(String(60), nullable=False) # steem_type:{_type}']

    # optional< public_key_type>
    elif _type == 'optional< public_key_type>':
        return [f'{name} = Column(String(60)) # steem_type:{_type}']

    # string type
    elif _type == 'string':
        return [f'{name} = Column(Unicode(150)) # steem_type:{_type}']

    # boolean
    elif _type == 'bool':
        return [f'{name} = Column(Boolean) # steem_type:{_type}']

    # integers
    elif _type in SMALL_INT_TYPES:
        return [f'{name} = Column(SmallInteger) # steem_type:{_type}']
    elif _type in INT_TYPES:
        return [f'{name} = Column(Integer) # steem_type:{_type}']
    elif _type in BIG_INT_TYPES:
        return [f'{name} = Column(Numeric) # steem_type:{_type}']

    # vector< authority>
    elif _type == 'vector< authority>':
        return [f'{name} = Column(String(100)) # steem_type:{_type}']

    # vector< char>
    elif _type == 'vector< char>':
        return [f'{name} = Column(String(100)) # steem_type:{_type}']

    # block_id_type
    elif _type == 'block_id_type':
        return [f'{name} = Column(String(40)) # steem_type:{_type}']

    # vector< beneficiary_route_type>
    elif _type == 'vector< beneficiary_route_type>':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # flat_set< account_name_type>
    elif _type == 'flat_set< account_name_type>':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # time_point_sec
    elif _type == 'time_point_sec':
        return [f'{name} = Column(DateTime) # steem_type:{_type}']

    # price
    elif _type == 'price':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # extensions_type
    elif _type == 'extensions_type' or _type == 'steemit::protocol::comment_options_extensions_type':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # authority
    elif _type == 'authority':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # signed_block_header
    elif _type == 'signed_block_header':
        return [f'{name} = Column(String(500)) # steem_type:{_type}']

    # chain_properties
    elif _type == 'chain_properties':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # pow
    elif _type == 'pow':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # steemit::protocol::pow2_work
    elif _type == 'steemit::protocol::pow2_work':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # pow2_input
    elif _type == 'pow2_input':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # fc::equihash::proof
    elif _type == 'fc::equihash::proof':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # default string
    else:
        return [f'{name} = Column(Unicode(100)) # steem_type:{_type} -> default']


def op_file(cls):
    return cls['name'].replace('_operation', '') + '.py'


def op_class_name(cls):
    op_name = cls['name']
    short_op_name = op_name.replace('_operation', '')
    parts = [s.title() for s in short_op_name.split('_')]
    if op_name in VIRTUAL_OPS_NAMES:
        parts.append('Virtual')
    parts.append('Operation')
    return ''.join(parts)


def op_old_table_name(op_name):
    table_name = OLD_TABLE_NAME_MAP.get(op_name)
    if not table_name:
        short_op_name = op_name.replace('_operation', '')
        table_name = f'sbds_tx_{p.plural(short_op_name)}'
    return table_name


def op_table_name(op_name):
    short_op_name = op_name.replace('_operation', '')
    if op_name in VIRTUAL_OPS_NAMES:
        return f'sbds_op_virtual_{p.plural(short_op_name)}'
    return f'sbds_op_{p.plural(short_op_name)}'


def iter_classes(header):
    for cls in header['classes']:
        yield cls


def iter_properties_keys(cls, keys=None):
    keys = keys or ('name', 'type')
    for prop in cls['properties']['public']:
        yield {k: prop[k] for k in keys}


def op_columns(cls):
    columns = []
    indent = '    '
    op_name = cls['name']
    props = iter_properties_keys(cls)
    for prop in props:
        name = prop['name']
        _type = prop['type']
        cols = get_columns(name, _type, op_name)
        columns.extend(f'{indent}{col}' for col in cols)
    return '\n'.join(columns)


def op_fields(cls):
    fields = []
    indent = '        '
    props = iter_properties_keys(cls)
    for prop in props:
        name = prop['name']
        _type = prop['type']
        if name == 'from':
            continue
        flds = get_fields(name, _type)
        fields.extend(f'{indent}{fld}' for fld in flds)
    return '\n'.join(fields)


def op_source(cls):
    source = virtual_op_source_map.get(cls['name'], '')
    if source:
        return f'''

    CPP Class Definition
    ======================
    {source}

    '''
    return ''


def get_op_example(op_name, db_url, table_name=None, cache_dir=None):
    if cache_dir:
        try:
            return _get_op_example_from_cache(op_name, cache_dir)
        except Exception as e:
            pass
    return ''


def _get_op_example_from_cache(op_name, cache_dir):
    with open(f'{cache_dir}/examples/{op_name}.json') as f:
        print(f'loading {op_name} example from cache', file=sys.stderr)
        return f.read()


def _get_op_exmaple_from_db(table_name, db_url):
    print('loading example from db', file=sys.stderr)
    op_block_query = f'SELECT {table_name}.block_num, transaction_num, operation_num, raw FROM {table_name} JOIN sbds_core_blocks ON {table_name}.block_num=sbds_core_blocks.block_num LIMIT 1;'
    proc_result = subprocess.run([
        'mysqlsh',
        '--json',
        '--uri', db_url,
        '--sqlc'],
        input=op_block_query.encode(),
        stdout=subprocess.PIPE)

    output = proc_result.stdout.decode().replace(BAD_MYSQLSH_OUTPUT, '')
    result_json = json.loads(output)
    transaction_num = result_json['rows'][0]['transaction_num']
    operation_num = result_json['rows'][0]['operation_num']
    block = json.loads(result_json['rows'][0]['raw'])
    example = block['transactions'][transaction_num - 1]['operations'][
        operation_num - 1][1]
    if example:
        return json.dumps(example, indent=2)
    return example


def op_class_operation_base(cls):
    name = cls['name']
    if name in VIRTUAL_OPS_NAMES:
        return 'BaseVirtualOperation'
    return 'BaseOperation'


def op_rel_import_dot(cls):
    name = cls['name']
    if name in VIRTUAL_OPS_NAMES:
        return '.'
    return ''


def write_class(path, text):
    p = Path(path)
    p.write_text(text)


def _generate_class(op_name, cls, db_url=None, cache_dir=None):
    if db_url:
        op_example = get_op_example(op_name, db_url, cache_dir=cache_dir)
    else:
        op_example = ''

    return class_template.format(
        op_name=op_name,
        op_class_name=op_class_name(cls),
        op_table_name=op_table_name(op_name),
        op_columns=reindent(str(op_columns(cls)), 4),
        op_fields=reindent(str(op_fields(cls)), 8),
        op_source=op_source(cls),
        op_example=addindent(str(op_example), 4),
        op_class_operation_base=op_class_operation_base(cls),
        op_rel_import_dot=op_rel_import_dot(cls)
    )


@click.group()
def codegen():
    """Query the Steem blockchain"""


@codegen.command(name='generate-classes')
@click.argument('header_file', type=click.File(mode='r'))
@click.option('--cache_dir', type=click.Path(file_okay=False))
@click.option('--db_url', type=click.STRING)
def generate_classes(header_file, cache_dir, db_url):
    header = json.load(header_file)
    base_path = os.path.dirname(header_file.name)
    for op_name, cls in header['classes'].items():
        filename = op_file(cls)
        path = os.path.join(base_path, filename)
        text = _generate_class(op_name, cls, db_url=db_url, cache_dir=cache_dir)
        write_class(path, text)


@codegen.command(name='generate-class')
@click.argument('op_name', type=click.STRING)
@click.argument('header_file', type=click.File(mode='r'))
@click.option('--cache_dir', type=click.Path(file_okay=False))
@click.option('--db_url', type=click.STRING)
def generate_class(op_name, header_file, cache_dir, db_url):
    header = json.load(header_file)
    base_path = os.path.dirname(header_file.name)

    if not op_name.endswith('_operation'):
        op_name = op_name + '_operation'
    cls = header['classes'][op_name]
    text = _generate_class(op_name, cls, db_url=db_url, cache_dir=cache_dir)
    #filename = op_file(cls)
    #path = os.path.join(base_path, filename)
    #write_class(path, text)
    click.echo(text, file=sys.stdout)


@codegen.command(name='generate-class-example')
@click.argument('op_name', type=click.STRING)
@click.argument('db_url', type=click.STRING)
def generate_class_example(op_name, db_url):
    op_example = get_op_example(op_name, db_url)
    click.echo(op_example, file=sys.stdout)


@codegen.command(name='generate-get-ops-in-block-example')
@click.argument('op_name', type=click.STRING)
@click.argument('db_url', type=click.STRING)
def generate_class_example(op_name, db_url):
    op_example = get_op_example(op_name, db_url)
    click.echo(op_example, file=sys.stdout)


if __name__ == '__main__':
    codegen()
