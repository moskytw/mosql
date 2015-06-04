#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the SQLite-specific stuff to :mod:`mosql.util`.

The usage:

::

    import mosql.sqlite

If you want to patch again:

::

    mosql.sqlite.patch()

It will replace the functions in :mod:`mosql.util` with its functions.
'''

def format_param(s=''):
    '''It formats the parameter of prepared statement.'''
    return ':%s' % s if s else '?'

def stringify_bool(b):
    '''It stringifies the bool.

    SQLite does not take ``TRUE`` and ``FALSE`` literals, only integers, so we
    return ``1`` and ``0`` instead.
    '''
    return '1' if b else '0'

import mosql.util

def patch():
    '''Applies the SQLite-specific functions again.

    .. versionadded:: 0.10
    '''
    mosql.util.format_param = format_param
    mosql.util.stringify_bool = stringify_bool

patch() # patch it when load this module

if __name__ == '__main__':
    import doctest
    doctest.testmod()
