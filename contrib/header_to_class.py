#!/usr/bin/env python

# coding=utf-8
import json
import os.path
from pathlib import Path

import click

from collections import defaultdict

# virtual operations
# https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/steem_virtual_operations.hpp
virtual_op_source_map = {
    'author_reward_operation':'''
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
    'liquidity_reward_operation':'''
    struct liquidity_reward_operation : public virtual_operation
   {
      liquidity_reward_operation( string o = string(), asset p = asset() )
      :owner(o), payout(p) {}

      account_name_type owner;
      asset             payout;
   };''',
    'interest_operation':'''
    struct interest_operation : public virtual_operation
   {
      interest_operation( const string& o = "", const asset& i = asset(0,SBD_SYMBOL) )
         :owner(o),interest(i){}

      account_name_type owner;
      asset             interest;
   };''',
    'fill_convert_request_operation':'''
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


class_template = '''
# coding=utf-8
import os.path

from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from toolz import get_in

from ... import Base
from ....enums import operation_types_enum
from ....field_handlers import amount_field
from ....field_handlers import amount_symbol_field
from ....field_handlers import comment_body_field
from ..base import BaseOperation

class {camel_op_name}(Base, BaseOperation):
    """
    
    {op_source}

    """
    
    __tablename__ = 'sbds_op_{op_name}s'
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

name_to_column_map = defaultdict(lambda: [])
name_to_column_map.update({
    'fee': ['Column(Numeric(15, 6), nullable=False)',
            'fee_symbol = Column(Unicode(5))'],
    'delegation': ['Column(Numeric(15, 6), nullable=False)'],
    'creator': ['Column(Unicode(50), nullable=False, index=True)'],
    'new_account_name': ['Column(Unicode(50), index=True)'],
    'owner_key': ['Column(Unicode(80), nullable=False)'],
    'active_key': ['Column(Unicode(80), nullable=False)'],
    'posting_key': ['Column(Unicode(80), nullable=False)'],
    'memo_key': ['Column(Unicode(250), nullable=False)'],
    'json_metadata': ['Column(UnicodeText)'],
    '_from': ["Column('from', Unicode(50), index=True)"],
    'request_id': ['Column(Integer)'],
    'permlink': ['Column(Unicode(512), nullable=False, index=True)'],
    'parent_author': ['Column(Unicode(50), index=True)'],
    'parent_permlink': ['Column(Unicode(512))'],
    'json': ['Column(UnicodeText)'],

})

type_to_column_map  = defaultdict(lambda: ['Column(Unicode(100)) # type'])
type_to_column_map.update({
    'account_name_type': ['Column(Unicode(50)) # account_name_type'],
    'asset': ['Column(Numeric(15, 6), nullable=False) # asset',
              '# asset_symbol = Column(Unicode(5)) # asset'],
    'string': ['Column(Unicode(150)) # string']
})


def read_json_file(ctx, param, f):
    return json.load(f)

def op_file(cls):
    return cls['name'].replace('_operation','') + '.py'


def op_class_name(cls):
    return ''.join(s.title() for s in cls['name'].split('_'))

def iter_classes(header):
    for cls in header['classes']:
        yield cls

def iter_properties_keys(cls, keys=None):
    keys = keys or ('name','type')
    for prop in cls['properties']['public']:
        yield {k:prop[k] for k in keys}

def op_columns(cls):
    columns = []
    indent = '    '
    props = iter_properties_keys(cls)
    for prop in props:
        name = prop['name']
        _type = prop['type']
        cols = name_to_column_map.get(name)
        if not cols:
            cols = type_to_column_map[_type]
        columns.append(f'{indent}{name} = {cols[0]}')
        if len(cols) > 1:
            for col in cols[1:]:
                columns.append(f'{indent}{col}')
    return '\n'.join(columns)

def op_fields(cls):
    fields = []
    indent = '        '
    props = iter_properties_keys(cls)
    for prop in props:
        name = prop['name']
        _type = prop['type']
        if _type == 'asset':
            # amount_field(x.get('amount'), num_func=float)
            fields.append(f"{indent}{name}=lambda x: amount_field(x.get('{name}'), num_func=float),")
            fields.append(f"{indent}{name}_symbol=lambda x: amount_symbol_field(x.get('{name}')),")
        elif name == 'body':
            #body = lambda x: comment_body_field(x['body']),
            fields.append(f"{indent}{name}=lambda x: comment_body_field(x.get('{name}')),")
        else:
            fields.append(f"{indent}{name}=lambda x: x.get('{name}'),")
    return '\n'.join(fields)

def op_source(cls):
    source =  virtual_op_source_map.get(cls['name'], '')
    if source:
        return  f'''
        
    CPP Class Definition
    ======================
    {source}
    
    '''
    return ''



def fix_bad_var_name(prop):
    if prop['name'] == 'from':
        prop['name'] = '_from'
    return prop


def write_class(path, text):
    p = Path(path)
    p.write_text(text)

@click.command(name='generate_classes')
@click.argument('infile', type=click.File(mode='r'), callback=read_json_file,
                default='-')
@click.argument('base_path', type=click.STRING)
def cli(infile, base_path):
    header = infile
    for op_name, cls in header['classes'].items():
        filename  = op_file(cls)
        path = os.path.join(base_path, filename)
        text = class_template.format(op_name=op_name,
                                     camel_op_name=op_class_name(cls),
                                     op_columns=op_columns(cls),
                                     op_fields=op_fields(cls),
                                     op_source=op_source(cls)
                                     )
        write_class(path,text)

if __name__ == '__main__':
    cli()
