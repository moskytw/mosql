#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import mosql

setup(

    name = 'mosql',
    version = mosql.__version__,
    description = "Build SQL with native Python data structure smoothly.",
    long_description = open('README.rst').read(),

    author = 'Mosky',
    author_email = 'mosky.tw@gmail.com',
    url = 'http://mosql.mosky.tw/',
    license = 'MIT',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages = find_packages(),
)

