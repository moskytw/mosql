#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains the builders of addational SQL statements.

.. deprecated:: 0.1.6
    Use :mod:`mosql.common` instead. It will be removed after 0.2.
'''

__all__ = ['or_', 'natural', 'left', 'right', 'inner', 'cross']

from .util import concat_by_or, build_where
from .common import join

def cross(table):
    '''It is a shortcut for the SQL statement, ``cross join ...`` .

    :rtype: str

    >>> print cross('table')
    CROSS JOIN "table"
    '''
    return join(table, type='cross')

def natural(table):
    '''It is a shortcut for the SQL statement, ``natural join ...`` .

    :rtype: str

    >>> print natural('table')
    NATURAL JOIN "table"
    '''
    return join(table, type='natural')

def inner(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``inner join ...`` .

    :rtype: str

    >>> print inner('table', using='c1')
    INNER JOIN "table" USING ("c1")
    '''
    return join(table, type='inner', on=on, using=using)

def left(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``left join ...`` .

    :rtype: str

    >>> print left('table', using='c1')
    LEFT JOIN "table" USING ("c1")
    '''
    return join(table, type='left', on=on, using=using)

def right(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``right join ...`` .

    :rtype: str

    >>> print right('table', using='c1')
    RIGHT JOIN "table" USING ("c1")
    '''
    return join(table, type='right', on=on, using=using)

def or_(*x, **format_spec):
    '''Concat expressions by operator, `OR`.

    :rtype: str

    The exmaples:

    >>> print or_("\\"x\\" = 'a'", '"y" > 1')
    ("x" = 'a') OR ("y" > 1)

    >>> print or_({'x': 'a'}, {'y >': 1})
    ("x" = 'a') OR ("y" > 1)

    >>> str_exp = build_where({'x': 'a', 'y': 'b'})
    >>> print or_(str_exp, {'z': 'c', 't >': 0})
    ("y" = 'b' AND "x" = 'a') OR ("t" > 0 AND "z" = 'c')
    '''

    return concat_by_or('(%s)' % build_where(i) for i in x)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
