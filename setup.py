#!/usr/bin/env python
import json
import os
from os.path import abspath, dirname

from setuptools import setup, find_packages

install_requires = []
tests_require = []

if os.path.isfile('Pipfile.lock'):
    with open('Pipfile.lock') as fd:
        lock_data = json.load(fd)
        install_requires = [
            package_name + package_data['version']
            for package_name, package_data in lock_data['default'].items()
        ]
        tests_require = [
            package_name + package_data['version']
            for package_name, package_data in lock_data['develop'].items()
        ]

setup(
    name='flox-jira',
    version='0.1',
    description='Jira integration for flox',
    packages=find_packages(where=dirname(abspath(__file__))),
    entry_points='''
        [flox.cli_plugins]
        jira=flox_jira.jira:jira

        [flox.cli_plugins.config]
        jira=flox_jira:config
        
        [flox.cli_plugins.services]
        jira=flox_jira:services
    ''',
    install_requires=install_requires,
    tests_require=tests_require,
    python_requires='>=3.6'
)
