# coding=utf-8
from setuptools import find_packages
from setuptools import setup
# yapf: disable
dev_requires = [
    'pep8',
    'pytest',
    'pytest-console-scripts',
    'pytest-pylint',
    'recommonmark',
    'sphinx',
    'sphinxcontrib-programoutput',
    'sphinxcontrib-restbuilder',
    'yapf'
]

tests_require = [
    'pep8',
    'pytest-pylint',
    'pytest-runner',
]

install_requires = [
    'boto3',
    'bottle',
    'bottle-sqlalchemy',
    'bottle_errorsrest',
    'certifi',
    'Click',
    'click-spinner',
    'langdetect',
    'maya',
    'mysqlclient',
    'python-json-logger',
    'requests==2.10.0',
    'rollbar',
    'sqlalchemy',
    'steem-piston==0.4.1',
    'toolz',
    'ujson',
    'urllib3',
    'w3lib'
]


setup(
    name='sbds',
    version='0.1',
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
        'ext_tests': tests_require
    },
    entry_points={
        'console_scripts': [
            'sbds=sbds.cli:sbds',
            'populate=sbds.storages.db.scripts.populate:populate'
        ]
    })
