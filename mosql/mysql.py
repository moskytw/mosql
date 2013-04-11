#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains the utils for MySQL.

After import it, it replaces the :py:func:`mosql.util.escape` with its :py:func:`mosql.mysql.escape`.'''

__all__ = ['escape']

ESCAPE_CHAR_MAP = {
        0x00 : r'\0',
        0x08 : r'\b',
        0x09 : r'\t',
        0x0a : r'\n',
        0x0d : r'\r',
        0x1a : r'\Z',
        0x22 : r'\"',
        0x25 : r'\%',
        0x27 : r"\'",
        0x5c : r'\\',
        0x5f : r'\_',
    }

def escape(s):
    '''It is the escaping function designed for the MySQL mode.

    >>> sql_tmpl = "SELECT * FROM member WHERE name = '%s' AND email = '...';"
    >>> val = "'; DROP TABLE member; --"
    >>> print sql_tmpl % escape(val)
    SELECT * FROM member WHERE name = '\'\;\ DROP\ TABLE\ member\;\ \-\-' AND email = '...';
    '''

    escaped_chars = []

    for c in s:

        if ord(c) >= 256:
            escaped_chars.append(c)
            continue

        if c.isalnum():
            escaped_chars.append(c)
            continue

        escaped_char = ESCAPE_CHAR_MAP.get(ord(c))
        escaped_chars.append('\\'+c if escaped_char is None else escaped_char)

    return ''.join(escaped_chars)

import mosql.util
mosql.util.escape = escape

if __name__ == '__main__':
    import doctest
    doctest.testmod()
