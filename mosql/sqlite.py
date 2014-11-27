#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the sqlite-specific stuff to :mod:`mosql.util`.

The usage:

::

    import mosql.sqlite

If you want to patch again:

::

    mosql.sqlite.patch()

.. versionadded:: 0.9.2

It will replace the functions in :mod:`mosql.util` with its functions.
'''

def format_param(s=''):
    '''It formats the parameter of prepared statement.'''
    return ':%s' % s if s else '?'

import mosql.util

def patch():
    mosql.util.format_param = format_param

patch() # patch it when load this module

if __name__ == '__main__':
    import doctest
    doctest.testmod()
