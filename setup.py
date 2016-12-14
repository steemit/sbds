from setuptools import setup
from setuptools import find_packages
setup(
    name='sbds',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'steem-piston==0.4.1',
        'websocket-client==0.37.0',
        'boto3',
        'python-json-logger',
        'requests'
    ],
    entry_points={'console_scripts': [
            'sbds=sbds.sbds:cli',
            'notify=sbds.notify:notify',
            's3=sbds.s3:s3'
    ]}
)
