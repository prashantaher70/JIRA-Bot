#!/usr/bin/env python

from distutils.core import setup

setup(
    name='OmniWheel',
    version='1.0',
    description='JIRA assistant',
    install_requires=[
        'Flask',
        'pymongo',
        'tlslite',
        'oauth2',
        'gevent-socketio',
        'gevent==1.1b4',
        'wit',
        'redis'
    ]
)