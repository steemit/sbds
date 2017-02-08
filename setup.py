# coding=utf-8
from setuptools import setup
from setuptools import find_packages
setup(
    name='sbds',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'pytest',
        'steem-piston==0.4.1',
        'boto3',
        'awscli',
        'python-json-logger',
        'requests==2.10.0',
        'mysqlclient',
        'sqlalchemy',
        'ujson',
        'bottle',
        'bottle-sqlalchemy',
        'urllib3',
        'elasticsearch-dsl>=2.0.0,<3.0.0',
        'certifi',
        'maya',
        'toolz',
        'w3lib',
        'langdetect',
        'lxml',
        'markdown'
    ],
    scripts=['sbds/storages/db/scripts/populate.sh',
             'sbds/storages/db/scripts/stream.sh'],
    entry_points={'console_scripts': [
        'sbds=sbds.cli:cli',
        'bulk-blocks=sbds.cli:bulk_blocks',
        'block-height=sbds.cli:block_height',
        'notify=sbds.notify:notify',
        's3=sbds.storages.s3.cli:s3',
        'db=sbds.storages.db.cli:db',
        'condense-error-files=sbds.cli:condense_error_files',
        'es=sbds.storages.elasticsearch.cli:es',
        'load-checkpoint-blocks=sbds.cli:load_blocks_from_checkpoints',
        'dev-server=sbds.http_server:dev_server'
    ]}
)
