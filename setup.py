# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='sbds',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'sbds=sbds.cli:sbds',
            'populate=sbds.storages.db.scripts.populate:populate',
        ],
    },
)
