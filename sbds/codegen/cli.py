# -*- coding: utf-8 -*-

import glob
import json
import sys

import click
import inflect
import os.path
import toolz

from collections import defaultdict
from jinja2 import Environment
from jinja2 import FileSystemLoader

INFLECTOR = inflect.engine()

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
HEADERS_PATH = os.path.join(BASE_PATH, 'headers')
TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates')
EXAMPLES_PATH = os.path.join(BASE_PATH, 'examples')

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


columns_map = defaultdict(lambda: [])
columns_map.update({
    'json_metadata': ['json_metadata = Column(JSONB) # name:json_metadata'],
    'from': ["_from = Column('from',UnicodeText) # name:from"],
    'json': ['json = Column(JSONB) # name:json'],
    'body': ['body = Column(UnicodeText) # name:body'],
    'json_meta': ['json_meta = Column(JSONB) # name:json_meta'],
    'memo': ['memo = Column(UnicodeText) # name:memo'],
    'permlink': ['permlink = Column(UnicodeText, index=True) # name:permlink'],
    'comment_permlink': ['permlink = Column(UnicodeText, index=True) # name:comment_permlink'],
    'parent_permlink': ['parent_permlink = Column(UnicodeText, index=True) # name:parent_permlink'],
    'title,comment_operation': ['title = Column(UnicodeText, index=True) # name:title,comment_operation'],
    'comment_permlink,curation_reward_operation': ['comment_permlink = Column(UnicodeText, index=True) # name:comment_permlink,curation_reward_operation'],
    'data,custom_binary_operation': ['data = Column(BYTEA()) # name: data,custom_binary_operation vector< char>'],
})


fields_map = defaultdict(lambda: [])
fields_map.update({
    'body': [f"body=lambda x: comment_body_field(x.get('body')), # name:body"],
    'json_metadata': [f"json_metadata=lambda x: json_string_field(x.get('json_metadata')), # name:json_metadata"],
    'json': [f"json=lambda x: json_string_field(x.get('json')), # name:json"],
    'posting': [f"posting=lambda x: json_string_field(x.get('posting')), # name:posting"],
    'active': [f"active=lambda x: json_string_field(x.get('active')), # name:active"],
    'json_meta': [f"json_meta=lambda x: json_string_field(x.get('json_meta')), # name:json_meta"],
    'data,custom_binary_operation': [f"data=lambda x: binary_field(x.get('data')),  # name: data,custom_binary_operation vector< char>"]
})


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


def get_fields(name, _type, op_name):

    # first: lookup by name,operation_name
    if fields_map.get(f'{name},{op_name}'):
        return fields_map.get(f'{name},{op_name}')

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
                f'from_symbol = Column(asset_types_enum, nullable=False) # steem_type:{_type}']
        return [
            f'{name} = Column(Numeric(20,6), nullable=False) # steem_type:asset',
            f'{name}_symbol = Column(asset_types_enum, nullable=False) # steem_type:{_type}']

    # account_name_type
    elif _type == 'account_name_type':
        return [
            f'{name} = Column(Text, nullable=True) # steem_type:{_type}']

    # flat_set< account_name_type>
    elif _type == 'flat_set< account_name_type>':
        return [f'{name} = Column(JSONB) # steem_type:{_type}']

    # public_key_type
    elif _type == 'public_key_type':
        return [f'{name} = Column(Text, nullable=False) # steem_type:{_type}']

    # optional< public_key_type>
    elif _type == 'optional< public_key_type>':
        return [f'{name} = Column(Text) # steem_type:{_type}']

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
        return [f'{name} = Column(UnicodeText) # steem_type:{_type}']

    # block_id_type (fc::ripemd160)
    elif _type == 'block_id_type':
        return [f'{name} = Column(Text) # steem_type:{_type}']

    # vector< beneficiary_route_type>
    elif _type == 'vector< beneficiary_route_type>':
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


def op_table_name(op_name):
    short_op_name = op_name.replace('_operation', '')
    if op_name in VIRTUAL_OPS_NAMES:
        return f'sbds_op_virtual_{INFLECTOR.plural(short_op_name)}'
    return f'sbds_op_{INFLECTOR.plural(short_op_name)}'


def iter_operation_classes(headers):
    if not isinstance(headers, (list, tuple)):
        headers = [headers]
    for header in headers:
        for name, cls in header['classes'].items():
            if 'operation' in name:
                yield name, cls


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


def is_account_name_reference(name, _type):
    return _type in {'account_name_type', 'flat_set< account_name_type>'}


def op_fields(cls):
    fields = []
    op_name = cls['name']
    props = iter_properties_keys(cls)
    for prop in props:
        name = prop['name']
        _type = prop['type']
        if name == 'from':
            continue
        flds = get_fields(name, _type, op_name)
        fields.extend(flds)
    return fields


def op_source(op_name, examples_path=None):
    try:
        with open(f'{examples_path}/{examples_path}.txt') as f:
            print(f'loading {op_name} source', file=sys.stderr)
            return f.read()
    except BaseException:
        return None


def get_op_example(op_name, cache_dir=None):
    if cache_dir:
        try:
            return _get_op_example_from_cache(op_name, cache_dir)
        except Exception as e:
            pass
    return ''


def _get_op_example_from_cache(op_name, cache_dir):
    with open(f'{cache_dir}/{op_name}.json') as f:
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


def operation_class_data(op_name, cls, cache_dir=None, refs=None):
    op_example = get_op_example(op_name, cache_dir=cache_dir)
    return dict(
        op_name=op_name,
        op_short_name=op_name.replace('_operation', ''),
        op_class_name=op_class_name(cls),
        op_table_name=op_table_name(op_name),
        op_columns=op_columns(cls),
        op_fields=op_fields(cls),
        op_source=op_source(op_name),
        op_example=op_example,
        op_class_operation_base=op_class_operation_base(cls),
        op_rel_import_dot=op_rel_import_dot(cls),
        refs=refs,
        op_is_virtual='virtual' in op_table_name(op_name)
    )


def _generate_account_refs(headers):
    refs = []
    block = {
        'name': 'block',
        'short_name': 'block',
        'class_name': 'Block',
        'table_name': 'sbds_core_blocks',
        'field_name': 'witness',
        'class_field_name': 'witness',
        'ref_name': 'sbds_core_blocks.witness',
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
                    'name': op_name,
                    'short_name': op_name.replace('_operation', ''),
                    'class_name': op_class_name(cls),
                    'table_name': op_table_name(op_name),
                    'columns': get_columns(name, _type, op_name),
                    'field_name': name,
                    'type': _type,
                    'class_field_name': class_field_name,
                    'ref_name': f'{op_table_name(op_name)}.{name}'
                })
    return refs


def load_files_from_path(path, glob_ptrn='*.json', recursive=False, file_mode='r'):
    return [open(f, mode=file_mode) for f in glob.glob(f'{path}/{glob_ptrn}', recursive=recursive)]


def load_json_files_from_path(path):
    return [json.load(f) for f in load_files_from_path(path)]


@click.group(name='codegen')
def cli():
    """Generate code to build apps on the Steemit Blockchain"""


@cli.command(name='generate-accounts-class')
@click.option('--headers_path', type=click.Path(exists=True, file_okay=False),
              default=HEADERS_PATH)
@click.option('--templates_path', type=click.Path(exists=True, file_okay=False),
              default=TEMPLATES_PATH)
def generate_accounts_class(headers_path, templates_path):
    header_files = load_json_files_from_path(headers_path)
    refs = _generate_account_refs(header_files)
    grouped_refs = toolz.groupby('short_name', refs)
    for name, ref_group in grouped_refs.items():
        grouped_refs[name] = frozenset(r['field_name'] for r in ref_group)

    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('meta/accounts_class.tmpl')
    click.echo(template.render(refs=refs, grouped_refs=grouped_refs))


@cli.command(name='generate-operations-view')
@click.option('--headers_path', type=click.Path(exists=True, file_okay=False),
              default=HEADERS_PATH)
@click.option('--templates_path', type=click.Path(exists=True, file_okay=False),
              default=TEMPLATES_PATH)
def generate_operations_view(headers_path, templates_path):
    header_files = load_json_files_from_path(headers_path)
    operation_classes = iter_operation_classes(header_files)

    all_tables = [op_table_name(op_name) for op_name, cls in operation_classes]
    virtual_tables = [t for t in all_tables if 'virtual' in t]
    real_tables = [t for t in all_tables if 'virtual' not in t]

    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('views/operations_view.tmpl')
    click.echo(
        template.render(
            all_tables=all_tables,
            virtual_tables=virtual_tables,
            real_tables=real_tables))


@cli.command(name='generate-operation')
@click.argument('op_name', type=click.STRING)
@click.option('--headers_path', type=click.Path(exists=True, file_okay=False),
              default=HEADERS_PATH)
@click.option('--examples_path', type=click.Path(exists=True, file_okay=False),
              default=EXAMPLES_PATH)
@click.option('--templates_path', type=click.Path(exists=True, file_okay=False),
              default=TEMPLATES_PATH)
def generate_operation(op_name, headers_path, examples_path, templates_path):
    header_files = load_json_files_from_path(headers_path)
    refs = toolz.groupby('name', _generate_account_refs(header_files))

    if not op_name.endswith('_operation'):
        op_name = op_name + '_operation'

    cls = None
    for header in header_files:
        if op_name not in header['classes']:
            continue
        cls = header['classes'][op_name]
    if not cls:
        raise ValueError(f'Unknown operation name:{op_name}')

    data = operation_class_data(op_name, cls, cache_dir=examples_path, refs=refs.get(op_name, []), )

    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('operations/operation_class.tmpl')
    click.echo(template.render(**data), file=sys.stdout)


@cli.command(name='generate-rules')
@click.option('--headers_path', type=click.Path(exists=True, file_okay=False),
              default=HEADERS_PATH)
@click.option('--templates_path', type=click.Path(exists=True, file_okay=False),
              default=TEMPLATES_PATH)
def generate_rules(headers_path, templates_path):
    header_files = load_json_files_from_path(headers_path)
    operation_classes = iter_operation_classes(header_files)

    all_tables = [op_table_name(op_name) for op_name, cls in operation_classes]

    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('rules.tmpl')
    click.echo(template.render(all_tables=all_tables))


@cli.command(name='generate-roles')
@click.option('--headers_path', type=click.Path(exists=True, file_okay=False),
              default=HEADERS_PATH)
@click.option('--templates_path', type=click.Path(exists=True, file_okay=False),
              default=TEMPLATES_PATH)
def generate_roles(headers_path, templates_path):
    header_files = load_json_files_from_path(headers_path)
    operation_classes = iter_operation_classes(header_files)

    all_tables = [op_table_name(op_name) for op_name, cls in operation_classes]

    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('roles.tmpl')
    click.echo(template.render(all_tables=all_tables))
