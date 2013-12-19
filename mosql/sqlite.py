#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the sqlite-specific stuff to :mod:`mosql.util`.

The usage:

::

    import mosql.sqlite

It will replace the functions in :mod:`mosql.util` with its functions.
'''

def format_param(s=''):
    '''It formats the parameter of prepared statement.

    >>> print format_param('name')
    :name

    >>> print format_param()
    ?
    '''
    return ':%s' % s if s else '?'

import mosql.util
mosql.util.format_param = format_param

if __name__ == '__main__':
    import doctest
    doctest.testmod()
