#!/usr/bin/env python
# -*- coding: utf-8 -*-

# coding=utf-8
import json
import os.path
import subprocess
import sys
import textwrap
import toolz
from jinja2 import Environment
from jinja2 import FileSystemLoader

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


columns_map = defaultdict(lambda: [])
columns_map.update({
    'json_metadata': ['json_metadata = Column(JSONB) # name:json_metadata'],
    'from': ["_from = Column('from',String(50), ForeignKey('sbds_meta_accounts.name')) # name:from"],
    'json': ['json = Column(JSONB) # name:json'],
    'body': ['body = Column(UnicodeText) # name:body'],
    'json_meta': ['json_meta = Column(JSONB) # name:json_meta'],
    'memo': ['memo = Column(UnicodeText) # name:memo'],
    'permlink': ['permlink = Column(Unicode(256), index=True) # name:permlink'],
    'comment_permlink': ['permlink = Column(Unicode(256), index=True) # name:comment_permlink'],
    'parent_permlink': ['parent_permlink = Column(Unicode(256), index=True) # name:parent_permlink'],
    'title,comment_operation': ['title = Column(Unicode(256), index=True) # name:title,comment_operation'],
    'comment_permlink,curation_reward_operation': ['comment_permlink = Column(Unicode(256), index=True) # name:comment_permlink,curation_reward_operation'],
})


fields_map = defaultdict(lambda: [])
fields_map.update({
    'body': [f"body=lambda x: comment_body_field(x.get('body')), # name:body"],
    'json_metadata':[f"json_metadata=lambda x: json_string_field(x.get('json_metadata')), # name:json_metadata"],
    'json':[f"json=lambda x: json_string_field(x.get('json')), # name:json"],
    'posting':[f"posting=lambda x: json_string_field(x.get('posting')), # name:posting"],
    'active':[f"active=lambda x: json_string_field(x.get('active')), # name:active"],
    'json_meta':[f"json_meta=lambda x: json_string_field(x.get('json_meta')), # name:json_meta"],
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
    'int8_t',
    'int16_t'
)

INT_TYPES = (
    'uint16_t',
    'int32_t'
)

BIG_INT_TYPES = (
    'uint64_t',
    'int64_t',
    'uint32_t',
)

JSONB_FIELD_NAMES = {
    'json_metadata',
    'json',
    'posting',
    'owner',
    'active',
    'json_meta'
}

JSONB_TYPES = {
    'vector< beneficiary_route_type>',
    'flat_set< account_name_type>',
    'price',
    'extensions_type',
    'authority',
    'optional< authority>',
    'vector< authority>',
    'chain_properties',
    'pow',
    'steemit::protocol::pow2_work',
    'pow2_input',
    'fc::equihash::proof',
    'signed_block_header',
    'steemit::protocol::comment_options_extensions_type'
}

ACCOUNT_NAME_TYPES = {
    'account_name_type'
    'flat_set< account_name_type>',
}

def get_fields(name, _type):

    # first: lookup by name,operation_name
    if fields_map.get(f'{name},{type}'):
        return fields_map.get(f'{name},{type}')

    # second: lookup by name
    if fields_map.get(name):
        return fields_map.get(name)

    # third: lookup by type
    fields = []
    if _type == 'asset':
        # amount_field(x.get('amount'), num_func=float)
        fields.append(
            f"{name}=lambda x: amount_field(x.get('{name}'), num_func=float), # steem_type:{_type}")
        fields.append(
            f"{name}_symbol=lambda x: amount_symbol_field(x.get('{name}')), # steem_type:{_type}")

    elif _type == 'time_point_sec':
        fields.append(
            f"{name}=lambda x: dateutil.parser.parse(x.get('{name}')), # steem_type:{_type}")

    elif _type in JSONB_TYPES:
        fields.append(f"{name}=lambda x:json_string_field(x.get('{name}')), # steem_type:{_type}")

    return fields


def get_columns(name, _type, op_name):
    # first: lookup by name,operation_name
    cols = columns_map.get(f'{name},{op_name}')

    # second: lookup by name
    if not cols:
        cols = columns_map.get(name)

    # third: lookup by type
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
        return [
            f'{name} = Column(String(16), ForeignKey("sbds_meta_accounts.name")) # steem_type:{_type}']

    # public_key_type
    elif _type == 'public_key_type':
        return [f'{name} = Column(String(60), nullable=False) # steem_type:{_type}']

    # optional< public_key_type>
    elif _type == 'optional< public_key_type>':
        return [f'{name} = Column(String(60)) # steem_type:{_type}']

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

    # authority
    elif _type == 'authority':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # vector< authority>
    elif _type == 'vector< authority>':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # vector< char>
    elif _type == 'vector< char>':
        return [f'{name} = Column(String(100)) # steem_type:{_type}']

    # block_id_type fc::ripemd160
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
    elif _type == 'extensions_type':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # steemit::protocol::comment_options_extensions_type
    elif _type == 'steemit::protocol::comment_options_extensions_type':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # authority
    elif _type == 'authority':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # optional< authority>
    elif _type == 'optional< authority>':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # signed_block_header
    elif _type == 'signed_block_header':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

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
        return [f'{name} = Column(UnicodeText) # steem_type:{_type} -> default']


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

def iter_operation_classes(header):
    for name, cls in header['classes'].items():
        if 'operation' in name:
            yield name,cls

def iter_properties_keys(cls, keys=None):
    keys = keys or ('name', 'type')
    for prop in cls['properties']['public']:
        yield {k: prop[k] for k in keys}


def op_columns(cls):
    columns = []
    op_name = cls['name']
    props = iter_properties_keys(cls)
    for prop in props:
        name = prop['name']
        _type = prop['type']
        cols = get_columns(name, _type, op_name)
        columns.extend(cols)
    return columns


def is_account_name_reference(name,_type):
    return _type == 'account_name_type'


def op_fields(cls):
    fields = []
    props = iter_properties_keys(cls)
    for prop in props:
        name = prop['name']
        _type = prop['type']
        if name == 'from':
            continue
        flds = get_fields(name, _type)
        fields.extend(flds)
    return fields


def op_source(cls):
    source = virtual_op_source_map.get(cls['name'], '')
    if source:
        return f'''

    CPP Class Definition
    ======================
    {source}

    '''
    return ''


def get_op_example(op_name, db_url=None, table_name=None, cache_dir=None):
    if cache_dir:
        try:
            return _get_op_example_from_cache(op_name, cache_dir)
        except Exception as e:
            pass
    elif db_url:
        pass
    return ''


def _get_op_example_from_cache(op_name, cache_dir):
    with open(f'{cache_dir}/examples/{op_name}.json') as f:
        print(f'loading {op_name} example from cache', file=sys.stderr)
        return f.read()


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


def _generate_class(op_name, cls, db_url=None, cache_dir=None, template_path=None):
    op_example = get_op_example(op_name, db_url=db_url, cache_dir=cache_dir)
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('operation_class.tmpl')

    return template.render(
        op_name=op_name,
        op_short_name=op_name.replace('_operation',''),
        op_class_name=op_class_name(cls),
        op_table_name=op_table_name(op_name),
        op_columns=op_columns(cls),
        op_fields=op_fields(cls),
        op_source=op_source(cls),
        op_example=op_example,
        op_class_operation_base=op_class_operation_base(cls),
        op_rel_import_dot=op_rel_import_dot(cls)
    )

def _generate_account_refs(header_files):
    headers = [json.load(f) for f in header_files]
    refs = []
    block = {
        'name': 'block',
        'short_name':'block',
        'class_name': 'Block',
        'table_name': 'sbds_core_blocks',
        'field_name': 'witness',
        'class_field_name': 'witness',
        'ref_name':   'sbds_core_blocks.witness',
    }
    refs.append(block)
    for header in headers:
        for op_name, cls in iter_operation_classes(header):
            props = iter_properties_keys(cls)
            for prop in props:
                name = prop['name']
                _type = prop['type']
                class_field_name = name
                if name == 'from':
                    class_field_name = '_from'
                if not is_account_name_reference(name, _type):
                    continue
                refs.append({
                    'name':       op_name,
                    'short_name': op_name.replace('_operation',''),
                    'class_name': op_class_name(cls),
                    'table_name': op_table_name(op_name),
                    'columns':    get_columns(name, _type, op_name),
                    'field_name': name,
                    'type':       _type,
                    'class_field_name': class_field_name,
                    'ref_name':   f'{op_table_name(op_name)}.{name}'
                })
    return refs


@click.group()
def codegen():
    """Generate SQLAlchemy ORM Classes For Steemit Blockchain Operations"""


@codegen.command(name='generate-account-class')
@click.argument('header_files', type=click.File(mode='r'), nargs=-1)
@click.option('--template_path',type=click.Path(exists=True,file_okay=False),
              default=os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates'))
def generate_account_class(header_files, template_path):
    refs = _generate_account_refs(header_files)

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('accounts.tmpl')
    grouped_refs = toolz.groupby('short_name', refs)
    ref_extractors = {}
    for name,ref_group in grouped_refs.items():
        grouped_refs[name] = frozenset(r['field_name'] for r in ref_group)
    click.echo(template.render(refs=refs, grouped_refs=grouped_refs))


@codegen.command(name='generate-account-references')
@click.argument('header_files', type=click.File(mode='r'), nargs=-1)
def generate_account_name_references(header_files):
    refs = _generate_account_refs(header_files)
    click.echo(json.dumps( toolz.groupby('name', refs)))


@codegen.command(name='generate-class')
@click.argument('op_name', type=click.STRING)
@click.argument('header_file', type=click.File(mode='r'))
@click.option('--cache_dir', type=click.Path(file_okay=False),
              default=os.path.abspath(os.path.join(os.path.dirname(__file__),'../build')))
@click.option('--template_path',type=click.Path(exists=True,file_okay=False),
              default=os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates'))
def generate_class(op_name, header_file, cache_dir, template_path):
    header = json.load(header_file)
    if not op_name.endswith('_operation'):
        op_name = op_name + '_operation'
    cls = header['classes'][op_name]
    text = _generate_class(op_name, cls, db_url=None, cache_dir=cache_dir, template_path=template_path)
    click.echo(text, file=sys.stdout)


@codegen.command(name='generate-class-example')
@click.argument('op_name', type=click.STRING)
@click.argument('db_url', type=click.STRING)
def generate_class_example(op_name, db_url):
    op_example = get_op_example(op_name, db_url)
    click.echo(op_example, file=sys.stdout)

if __name__ == '__main__':
    codegen()
