from setuptools import setup

setup(
    name='sbds',
    version='0.1',
    py_modules=['sbds'],
    install_requires=[
        'Click',
        'steem-piston'
    ],
    entry_points='''
        [console_scripts]
        sbds=sbds:cli
    ''',
)
