from setuptools import setup, find_packages


REQUIRED = [
    'aiodns',
    'aiofiles',
    'aiohttp',
    'aiomysql',
    'certifi',
    'click',
    'click-spinner',
    'cytoolz',
    'funcy',
    'janus',
    'jsonrpcserver',
    'langdetect',
    'maya',
    'mysqlclient',
    'pymysql',
    'python-json-logger',
    'rollbar',
    'sqlalchemy',
    'structlog',
    'toolz',
    'ujson',
    'urllib3',
    'uvloop',
    'w3lib',
    'jsonrpcclient',
    'python-rapidjson',
    'aiopg',
    'colorama',
    'tqdm',
    'python-dateutil',
    'requests',
    'ipython',
    'aiotask-context',
    'asyncpg',
    'jinja2',
    'sqlalchemy-utils',
    'serpy',
    'psycopg2-binary',
    'inflect'
]


DEV_REQUIRES = [
    'ipython',
    'recommonmark',
    'sphinx',
    'sphinxcontrib-programoutput',
    'sphinxcontrib-restbuilder',
    'isort',
    'pre-commit',
    'autoflake',
    'pylint',
    'vulture',
    'mypy',
    'python-rapidjson',
    'inflect'
]

TEST_REQUIRES = [
    'autopep8',
    'pep8',
    'pytest',
    'pytest-console-scripts',
    'pytest-docker',
    'pytest-pylint',
    'yapf'
]

setup(
    name='sbds',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIRED,
    extras_require={
        'dev': DEV_REQUIRES + TEST_REQUIRES,
        'test': TEST_REQUIRES,
    },
    tests_require=TEST_REQUIRES,
    entry_points={
        'console_scripts': [
            'sbds=sbds.cli:sbds',
            'populate=sbds.storages.db.scripts.populate:populate',
        ],
    },
)
