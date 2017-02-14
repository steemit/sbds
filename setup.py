# coding=utf-8
from setuptools import find_packages
from setuptools import setup

# yapf: disable
setup(
    name='sbds',
    version='0.1',
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest',
                   'pep8',
                   'pytest-pylint',
                   'yapf',
                   'sphinx',
                   'recommonmark',
                   'sphinxcontrib-restbuilder',
                   'sphinxcontrib-programoutput'],
    install_requires=[
        'Click',
        'steem-piston==0.4.1',
        'boto3',
        'python-json-logger',
        'requests==2.10.0',
        'mysqlclient',
        'sqlalchemy',
        'ujson',
        'bottle',
        'bottle-sqlalchemy',
        'urllib3',
        'certifi',
        'maya',
        'toolz',
        'w3lib',
        'langdetect',
        'yapf'
    ],
    scripts=['sbds/storages/db/scripts/populate.sh'],
    entry_points={
        'console_scripts': [
            'sbds=sbds.cli:sbds',
            'dev-server=sbds.http_server:dev_server'
        ]
    })
