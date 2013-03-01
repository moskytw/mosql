#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .util import *

join_tmpl = SQLTemplate(
    ('<type>', ),
    ('join'  , '<table>'),
    ('on'    , '<on>'),
    ('using' , '<using>'),
)

def join(table, on=None, using=None, type=None, **fields):
    '''It is a shortcut for the SQL statement, ``join ...`` .

    :param type: It can be 'cross', 'natural', 'inner', 'left' or 'right'.
    :type type: str
    :rtype: str

    Without giving ``type``, it determines type automatically. It uses `left` join by default:

    >>> print join('another', 'table.c1 = another.c1')
    LEFT JOIN another ON table.c1 = another.c1

    >>> print join('another', ('table.c1 = another.c1', 'table.c2 = another.c2'))
    LEFT JOIN another ON table.c1 = another.c1 AND table.c2 = another.c2

    >>> print join('table', using='c1')
    LEFT JOIN table USING (c1)

    >>> print join('table', using=('c1', 'c2'))
    LEFT JOIN table USING (c1, c2)

    But if you give ``table`` only, it will switch to `natural` join.

    >>> print join('table')
    NATURAL JOIN table

    All of the fields:

    >>> print join_tmpl
    SQLTemplate(('<type>',), ('join', '<table>'), ('on', '<on>'), ('using', '<using>'))

    .. seealso::
        :py:func:`~sql.cross`, :py:func:`~sql.natural`, :py:func:`~sql.inner`, :py:func:`~sql.left` and :py:func:`~sql.right`

    '''

    fields['table'] = table

    if on:
        fields['on'] = on
    if using:
        fields['using'] = using

    if type:
        fields['type'] = type
    else:
        if on or using:
            fields['type'] = 'left'
        else:
            fields['type'] = 'natural'

    return join_tmpl.format_from_dict(fields)

def cross(table):
    '''It is a shortcut for the SQL statement, ``cross join ...`` .

    :rtype: str

    >>> print cross('table')
    CROSS JOIN table
    '''
    return join(table, type='cross')

def natural(table):
    '''It is a shortcut for the SQL statement, ``natural join ...`` .

    :rtype: str

    >>> print natural('table')
    NATURAL JOIN table
    '''
    return join(table, type='natural')

def inner(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``inner join ...`` .

    :rtype: str

    >>> print inner('table', using='c1')
    INNER JOIN table USING (c1)
    '''
    return join(table, type='inner', on=on, using=using)

def left(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``left join ...`` .

    :rtype: str

    >>> print left('table', using='c1')
    LEFT JOIN table USING (c1)
    '''
    return join(table, type='left', on=on, using=using)

def right(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``right join ...`` .

    :rtype: str

    >>> print right('table', using='c1')
    RIGHT JOIN table USING (c1)
    '''
    return join(table, type='right', on=on, using=using)

def or_(*x, **format_spec):
    '''Concat expressions by operator, `OR`.

    :rtype: str

    The exmaples:

    >>> print or_("x = 'a'", 'y > 1')
    (x = 'a') OR (y > 1)

    >>> print or_({'x': 'a'}, {'y >': 1})
    (x = 'a') OR (y > 1)

    >>> str_exp = dumps({'x': 'a', 'y': 'b'}, condition=True)
    >>> print or_(str_exp, {'z': 'c', 't >': 0})
    (y = 'b' AND x = 'a') OR (t > 0 AND z = 'c')
    '''

    return ' OR '.join('(%s)' % dumps(i, condition=True, **format_spec) for i in x)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
