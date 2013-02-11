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

def stringify(obj, str_func=str):
    '''It stringifies an object.

    Examples:

        'str'      -> 'str'
        1          -> '1'
        ('x', 'y') -> 'x, y'
        {'a': 'b'} -> "x='y'"
        callable   -> stringify(callable())
    '''

    if callable(obj):
        return stringify(obj(), str_func)
    elif hasattr(obj, 'items'):
        return ', '.join('%s=%s' % (stringify(k), quotes_stringify(v)) for k, v in obj.items())
    elif hasattr(obj, '__iter__'):
        return ', '.join(stringify(item, str_func) for item in obj)

    return str_func(obj)

def escape_single_quotes(s):
    return s.replace("'", "''")

def quotes_stringify(obj):
    return stringify(obj, lambda x: "'%s'" % escape_single_quotes(str(x)))

def parentheses_stringify(obj):
    return '(%s)' % stringify(obj)

def parentheses_quotes_stringify(obj):
    return '(%s)' % quotes_stringify(obj)

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
    print '# test quotes_stringify'
    print quotes_stringify('str')
    print quotes_stringify(123)
    print quotes_stringify(('hello', 'world'))
    print
    print '# test parentheses_stringify'
    print parentheses_stringify('str')
    print parentheses_stringify(123)
    print parentheses_stringify(('hello', 'world'))
    print
    print '# test parentheses_quotes_stringify'
    print parentheses_quotes_stringify('str')
    print parentheses_quotes_stringify(123)
    print parentheses_quotes_stringify(('hello', 'world'))
    print
