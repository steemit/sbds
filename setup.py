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
        'urllib3'
    ],
    scripts=['sbds/scripts/populate-sbds.sh'],
    entry_points={'console_scripts': [
        'sbds=sbds.cli:cli',
        'block-height=sbds.cli:block_height',
        'notify=sbds.notify:notify',
        's3=sbds.storages.s3.cli:s3',
        'db=sbds.storages.db.cli:db',
        'dev-server=sbds.http_server:dev_server'
    ]}
)
