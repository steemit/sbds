# coding=utf-8
from setuptools import find_packages
from setuptools import setup

dev_requires = [
    'pytest',
    'pep8',
    'pytest-pylint',
    'yapf',
    'sphinx',
    'recommonmark',
    'sphinxcontrib-restbuilder',
    'sphinxcontrib-programoutput',
    'pytest-console-scripts'
]

tests_require = [
    'pytest-runner',
    'pep8',
    'pytest-pylint',

]

install_requires = [
        'Click',
        'click-spinner',
        'steem-piston==0.4.1',
        'boto3',
        'python-json-logger',
        'requests==2.11.1',
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
        'bottle_errorsrest',
        'rollbar'
    ]

# yapf: disable
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
