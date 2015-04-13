#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the MySQL-specific stuff to :mod:`mosql.util`.

The usage:

::

    import mosql.mysql

If you want to patch again:

::

    mosql.mysql.patch()

It will replace the functions in :mod:`mosql.util` with its functions.
'''

import mosql.util

char_escape_map = {
    # The following 7 chars is escaped in MySQL Connector/C (0.6.2)
    '\0' : r'\0',
    '\n' : r'\n',
    '\r' : r'\r',
    '\\' : r'\\',
    '\'' : r'\'',
    '\"' : r'\"',
    '\x1A' : r'\Z',
    # The following 4 chars is escaped in OWASP Enterprise Security API (1.0)
    '\b' : r'\b',
    '\t' : r'\t',
    #'%'  : r'\%',
    #'_'  : r'\_',
    # The above 2 chars shouldn't be escaped, because '\%' and '\_' evaluate
    # to string '\%' and '\_' outside of pattern-matching contexts. Programmers
    # should take responsibility for escaping them in pattern-matching contexts.
}

def escape(s):
    r'''This function escapes the `s` into a executable SQL.

    >>> print(escape('\0\n\r\\\'\"\x1A\b\t'))
    \0\n\r\\\'\"\Z\b\t

    >>> tmpl = "select * from person where person_id = '%s';"
    >>> evil_value = "' or true; --"

    >>> print(tmpl % escape(evil_value))
    select * from person where person_id = '\' or true; --';
    '''
    global char_escape_map
    return ''.join(char_escape_map.get(c) or c for c in s)

def fast_escape(s):
    '''This function only escapes the ``\`` (backslash) and ``'``
    (single-quote).

    It is enough for security and correctness, and it is faster 50x than using
    the :func:`escape`, so it is used for replacing the
    :func:`mosql.util.escape` after you import this module.
    '''

    # We don't need to check the null byte here, because MySQL can handle the
    # null byte in value correctly.
    return s.replace('\\', '\\\\').replace("'", r"\'")

def format_param(s=''):
    '''This function always returns ``'%s'``, so it makes you can use the
    prepare statement with MySQLdb.'''
    return '%s'

def delimit_identifier(s):
    '''It encloses the identifier, `s`, by ````` (back-quote).'''
    mosql.util.raise_for_null_byte(s)
    return '`%s`' % s

def escape_identifier(s):
    '''It escapes the ````` (back-quote) in the identifier, `s`.'''
    return s.replace('`', '``')

def patch():
    '''Applies the MySQL-specific functions again.

    .. versionadded:: 0.10
    '''
    mosql.util.escape = fast_escape
    mosql.util.format_param = format_param
    mosql.util.delimit_identifier = delimit_identifier
    mosql.util.escape_identifier = escape_identifier

patch() # patch it when load this module

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    #from timeit import timeit
    #from functools import partial

    #timeit = partial(timeit, number=100000)
    #bytes = ''.join(chr(i) for i in range(256))

    #def _escape(s):
    #    return s.replace("'", "''")

    #print timeit(lambda: _escape(bytes))
    ## -> 0.118767976761

    #print timeit(lambda: escape(bytes))
    ## -> 7.97847890854

    #print timeit(lambda: fast_escape(bytes))
    ## -> 0.155963897705
