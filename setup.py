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
        'websocket-client==0.37.0',
        'boto3',
        'python-json-logger',
        'requests==2.10.0',
        'mysqlclient',
        'sqlalchemy',
        'ujson',
        'bottle',
        'urllib3',
        'elasticsearch-dsl>=2.0.0,<3.0.0',
        'certifi',
        'maya',
        'psycopg2'
    ],
    scripts=['sbds/storages/db/scripts/populate.sh',
             'sbds/scripts/stream.sh'],
    entry_points={'console_scripts': [
        'sbds=sbds.cli:cli',
        'bulk-blocks=sbds.cli:bulk_blocks',
        'block-height=sbds.cli:block_height',
        'notify=sbds.notify:notify',
        's3=sbds.storages.s3.cli:s3',
        'db=sbds.storages.db.cli:db',
        'es=sbds.storages.elasticsearch.cli:es',
        'load-checkpoint-blocks=sbds.cli:load_blocks_from_checkpoints',
        'dev-server=sbds.http_server:dev_server'
    ]}
)
