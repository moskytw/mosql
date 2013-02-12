#!/usr/bin/env python
# -*- coding: utf-8 -*-

def quoted(s):
    '''Quote a string and escape the single quotes.

    >>> print quoted('string without single quote')
    'string without single quote'

    >>> print quoted("' or 1=1 --")
    '\'' or 1=1 --'

    >>> print quoted("' DROP TABLE user; --")
    '\'' DROP TABLE user; --'
    '''
    return "'%s'" % s.replace("'", "''")

ENCODING = 'UTF-8'

def stringify(x, quote=False):
    '''Convert any object ``x`` to SQL's representation.

    It supports:

    - ``None`` (as ``null`` in SQL)
    - ``unicode``
    - number (include ``int`` and ``float``)
    - ``dict``
    - iterable (include ``tuple``, ``list``, ...)

    It returns None if it doesn't know how to convert.

    >>> print stringify('It is a string.')
    It is a string.

    >>> print stringify('It is a string.', quote=True)
    'It is a string.'

    >>> print stringify(('string', 123, 123.456))
    string, 123, 123.456

    >>> print stringify(('string', 123, 123.456), quote=True)
    'string', 123, 123.456

    >>> print stringify(None)
    null

    >>> print stringify(None, quote=True)
    null

    >>> print stringify(123)
    123

    >>> print stringify(123, quote=True)
    123

    >>> print stringify({'number': 123})
    number=123

    >>> print stringify({'number': 123}, quote=True)
    number=123

    >>> print stringify({'key': 'value'})
    key='value'

    >>> print stringify({'key': 'value'}, quote=True)
    key='value'
    '''

    if x is None:
        return 'null'

    if isinstance(x, (int, float, long)):
        return str(x)

    if isinstance(x, unicode):
        x = x.encode(ENCODING)

    if isinstance(x, str):
        s = x
        if quote:
            s = quoted(x)
        return s

    if hasattr(x, 'items'):
        return ', '.join('%s=%s' % (stringify(k), stringify(v, quote=True)) for k, v in x.items())

    if hasattr(x, '__iter__'):
        strs = (stringify(i, quote) for i in x)
        return ', '.join(strs)

def stringify_columns(iterable):
    '''It is a customized stringify function for ``insert`` in SQL.

    >>> print stringify_columns(('string', 123, 123.456))
    (string, 123, 123.456)

    >>> print stringify_columns('any else')
    None
    '''
    if hasattr(iterable, '__iter__'):
        return '(%s)' % stringify(iterable)

def stringify_values(iterable):
    '''It is a customized stringify function for ``insert`` in SQL.

    >>> print stringify_values(('string', 123, 123.456))
    ('string', 123, 123.456)

    >>> print stringify_columns('any else')
    None
    '''
    if hasattr(iterable, '__iter__'):
        return '(%s)' % ', '.join(stringify(x, quote=True) for x in iterable)

class SQL(dict):

    @classmethod
    def insert(cls, table):
        sql = cls(
            ('insert into', '<table>'),
            ('<columns>', ),
            ('values', '<values>')
        )
        return sql

    @classmethod
    def select(cls, *fields):
        sql = cls(
            ('select', '<select>'),
            ('from', '<table>'),
            ('where', '<where>'),
            ('order by', '<order_by>'),
            ('<asc>', ),
            ('<desc>', ),
            ('limit', '<limit>'),
            ('offset', '<offset>')
        )
        return sql

    @classmethod
    def update(cls, table):
        sql = cls(
            ('update', '<table>'),
            ('set', '<set>'),
            ('where', '<where>')
        )
        return sql

    @classmethod
    def delete(cls, table):
        sql = cls(
            ('delete from', '<table>'),
            ('where', '<where>')
        )
        return sql

    def __init__(self, *template_groups):
        self.template_groups = template_groups

    def __str__(self):
        pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
