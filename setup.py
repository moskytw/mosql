#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import mosql


with open('README.rst', 'rb') as f:
    README = f.read()

# We want README to be a str, no matter it is byte or text. 'rb' reads bytes,
# so we need extra conversion on Python 3. On Python 2 bytes is synonym to str,
# and we're good.
if not isinstance(README, str):
    README = README.decode('utf-8')


setup(
    name='mosql',
    version=mosql.__version__,
    description='Build SQL with native Python data structure smoothly.',
    long_description=README,
    author='Mosky',
    author_email='mosky.tw@gmail.com',
    url='http://mosql.mosky.tw/',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['oldtests']),
    zip_safe=True,
)
