#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applys the MySQL-specific stuff to :mod:`mosql.util`.

Usage:

::

    import mosql.mysql

It replaces the function in :mod:`mosql.util` with it.
'''

def delimit_identifier(s):
    '''Enclose the identifier, `s`, by ` (back-quote).'''
    return '`%s`' % s

def escape_identifier(s):
    '''Escape the ` (back-quote) in the identifier, `s`.'''
    return s.replace('`', '``')

import mosql.util
mosql.util.delimit_identifier = delimit_identifier
mosql.util.escape_identifier = escape_identifier

if __name__ == '__main__':
    pass
