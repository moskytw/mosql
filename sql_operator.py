#!/usr/bin/env python
# -*- coding: utf-8 -*-

EMPTY = object()

def to_keyword(key):
    '''It converts the attribute name to the SQL keyword.

    Examples:

        from_    -> form
        order_by -> order by
        values_  -> values
    '''
    return key.replace('_', ' ').rstrip()

def escape_single_quotes(s):
    return s.replace("'", "''")

ENCODING = 'utf-8'

def stringify(obj, escape_it=False):
    '''It stringifies an object.

    Examples:

        'str'      -> 'str'
        1          -> '1'
        ('x', 'y') -> 'x, y'
        {'a': 'b'} -> "x='y'"
        callable   -> stringify(callable())
    '''

    if isinstance(obj, unicode):
        return obj.encode(ENCODING)
    elif callable(obj):
        return stringify(obj(), escape_it)
    elif hasattr(obj, 'items'):
        return ', '.join('%s=%s' % (stringify(k, escape_it=False), stringify(v, escape_it=True)) for k, v in obj.items())
    elif hasattr(obj, '__iter__'):
        return ', '.join(stringify(item, escape_it) for item in obj)

    if isinstance(obj, str):
        if escape_it:
            return "'%s'" % escape_single_quotes(obj)
        else:
            return obj
    else:
        return str(obj)

def param(key):
    return '?'

def eq(key, value=EMPTY):
    if value is EMPTY:
        value = param(key)
    else:
        value = "'%s'" % escape_single_quotes(value)
    return '%s=%s' % (key, value)

if __name__ == '__main__':

    print '# test eq'
    print eq('key')
    print eq('key', 'value')
    print
    print '# test stringify'
    print stringify('str')
    print stringify(123)
    print stringify(('hello', 'world'))
    print stringify({'hello': 'world', 'number': 123})
    print
