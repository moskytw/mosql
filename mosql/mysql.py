#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applys the MySQL-specific stuff to :mod:`mosql.util`.

Usage:

::

    import mosql.mysql

It will replace the function in :mod:`mosql.util` with it.
'''

char_escape_map = {
    # escape chars in the official libaray
    '\0' : r'\0',
    '\n' : r'\n',
    '\r' : r'\r',
    '\\' : r'\\',
    '\"' : r'\"',
    '\x1A' : r'\Z',
    # escape chars in the esapi of OWASP
    '\b' : r'\b',
    '\t' : r'\t',
    '\'' : r'\'',
    '%'  : r'\%',
    '_'  : r'\_',
}

def escape(s):
    '''The function is designed for MySQL.

    >>> tmpl = "select * from person where person_id = '%s';"
    >>> evil_value = "' or true; --"

    >>> print tmpl % escape(evil_value)
    select * from person where person_id = '\\'\ or\ true\;\ \-\-';
    '''

    global char_escape_map

    escapes = []

    for c in s:

        if ord(c) >= 256:
            # c is not a 8-bit char
            escapes.append(c)
            continue

        if c.isalnum():
            escapes.append(c)
            continue

        escape = char_escape_map.get(c)
        escapes.append(escape if escape else c)

    return ''.join(escapes)

def delimit_identifier(s):
    '''Enclose the identifier, `s`, by ` (back-quote).'''
    return '`%s`' % s

def escape_identifier(s):
    '''Escape the ` (back-quote) in the identifier, `s`.'''
    return s.replace('`', '``')

import mosql.util

mosql.util.escape = escape
mosql.util.delimit_identifier = delimit_identifier
mosql.util.escape_identifier = escape_identifier

if __name__ == '__main__':
    import doctest
    doctest.testmod()
