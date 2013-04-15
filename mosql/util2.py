#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'Clause', 'Statement',
    'escape', 'stringify_bool', 'delimit_identifier', 'escape_identifier',
    'raw', 'default',
    'qualifier', 'value', 'identifier', 'paren',
    'aggregater',
    'concat_by_comma', 'concat_by_and', 'concat_by_space', 'concat_by_or',
    'allowed_operators',
    'build_where', 'build_set',
]

from functools import wraps
from datetime import datetime, date, time

def escape(s):
    return s.replace("'", "''")

def stringify_bool(b):
    return 'TRUE' if b else 'FALSE'

def delimit_identifier(s):
    return '"%s"' % s

def escape_identifier(s):
    return s.replace('"', '""')

class raw(str):

    def __repr__(self):
        return 'raw(%s)' % self

default = raw('DEFAULT')

def _is_iterable_not_str(x):
    return not isinstance(x, basestring) and hasattr(x, '__iter__')

def qualifier(f):

    @wraps(f)
    def qualifier_wrapper(x):
        if isinstance(x, raw):
            return x
        elif _is_iterable_not_str(x):
            return map(f, x)
        else:
            return f(x)

    return qualifier_wrapper

@qualifier
def value(x):

    if isinstance(x, (datetime, date, time)):
        x = str(x)

    if isinstance(x, basestring):
        return "'%s'" % escape(x)
    elif x is None:
        return 'NULL'
    elif isinstance(x, bool):
        return stringify_bool(x)
    else:
        return str(x)

@qualifier
def identifier(s):
    if delimit_identifier is None:
        return s
    else:
        return delimit_identifier(escape_identifier(s))

@qualifier
def paren(s):
    return '(%s)' % s

def aggregater(f):

    @wraps(f)
    def aggregater_wrapper(x):
        if _is_iterable_not_str(x):
            return f(x)
        else:
            return x

    return aggregater_wrapper

@aggregater
def concat_by_and(i):
    return ' AND '.join(i)

@aggregater
def concat_by_or(i):
    return ' OR '.join(i)

@aggregater
def concat_by_space(i):
    return ' '.join(i)

@aggregater
def concat_by_comma(i):
    return ', '.join(i)

allowed_operators = set([
    '<', '>', '<=', '>=', '=', '<>', '!=',
    'IS', 'IS NOT',
    'IN', 'NOT IN',
    'LIKE', 'NOT LIKE',
    'SIMILAR TO', 'NOT SIMILAR TO',
    '~', '~*', '!~', '!~*',
])

def _to_pairs(x):

    if hasattr(x, 'iteritems'):
        x = x.iteritems()
    elif hasattr(x, 'items'):
        x = x.items()

    return x

@aggregater
def build_where(x):

    ps = _to_pairs(x)

    pieces = []

    for k, v in ps:

        # split the op out
        op = None
        if not isinstance(k, raw):
            space_pos = k.find(' ')
            if space_pos != -1:
                k, op = k[:space_pos], k[space_pos+1:]

        # qualify the k, op and v

        k = identifier(k)

        if not op:
            if _is_iterable_not_str(v):
                op = 'IN'
            elif v is None:
                op = 'IS'
            else:
                op = '='
        else:
            op = op.upper()
            if allowed_operators is not None:
                assert op in allowed_operators, 'the operator is not allowed: %r' % op

        v = value(v)
        if _is_iterable_not_str(v):
            v = paren(concat_by_comma(v))

        pieces.append('%s %s %s' % (k, op, v))

    return concat_by_and(pieces)

@aggregater
def build_set(x):

    ps = _to_pairs(x)

    pieces = []
    for k, v in ps:
        pieces.append('%s=%s' % (identifier(k), value(v)))

    return concat_by_comma(pieces)

# NOTE: To keep simple, the below classes shouldn't rely on the above functions

class Clause(object):

    def __init__(self, prefix, formatters):
        self.prefix = prefix.upper()
        self.formatters = formatters

    def format(self, x):
        for formatter in self.formatters:
            x = formatter(x)
        return '%s %s' % (self.prefix, x)

    def __repr__(self):
        return 'Clause(%s, %s)' % (self.prefix, self.formatters)

class Statement(object):

    def __init__(self, clauses):
        self.clauses = clauses

    def format(self, clause_args):

        pieces = []
        for clause in self.clauses:
            arg = clause_args.get(clause.prefix.lower().replace(' ', '_'))
            if arg is not None:
                pieces.append(clause.format(arg))
        return ' '.join(pieces)

    def __repr__(self):
        return 'Statement(%s)' % self.clauses

if __name__ == '__main__':

    # insert

    single_identifier = (identifier, )
    identifier_list = (identifier, concat_by_comma)

    insert_into = Clause('insert into', single_identifier)
    columns     = Clause('', (identifier, concat_by_comma, paren))
    values      = Clause('', (value, concat_by_comma, paren))
    returning   = Clause('returning', identifier_list)

    insert_into_stat = Statement([insert_into, columns, values, returning])

    # select

    single_value = (value, )
    where_list  = (build_where, )
    statement_list  = (concat_by_space, )

    select   = Clause('select'  , identifier_list)
    from_    = Clause('from'    , identifier_list)
    joins    = Clause(''        , statement_list)
    where    = Clause('where'   , where_list)
    group_by = Clause('group by', identifier_list)
    having   = Clause('having'  , where_list)
    order_by = Clause('order by', identifier_list)
    limit    = Clause('limit'   , single_value)
    offset   = Clause('offset'  , single_value)

    select_stat = Statement([select, from_, joins, where, group_by, having, order_by, limit, offset])

    # TODO: update
    # TODO: delete from
    # TODO: join, or_

    # tests

    print select_stat.format({'select': raw('*'), 'from': 'person', 'where': {'person_id like': 'me'}})
    print select_stat.format({'select': raw('*'), 'from': 'person', 'where': {'name': None}})
    print select_stat.format({'select': raw('*'), 'from': 'person', 'where': {'person_id not in': ['andy', 'bob']}})
    print select_stat.format({'select': raw('*'), 'from': 'person', 'where': (('person_id', 'mosky'), ('name', 'Mosky Liu'))})
    print select_stat.format({'select': raw('*'), 'from': 'person', 'where': 'person_id = any (select person_id from person)'})

    def select(table, where=None, select=raw('*'), **clause_args):

        clause_args['from'] = table
        clause_args['where'] = where
        clause_args['select'] = select

        return select_stat.format(clause_args)

    print select('person', {'person_id': 'mosky'})
    print select('person', {raw("function(x)"): 'mosky'})
    #print select('person', {"person_id = '' OR true; --": 'mosky'})
    # -> AssertionError: the operator is not allowed: "= '' OR TRUE; --"

    #from timeit import timeit

    #print timeit(lambda: select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    # -> 40.8449561596
    # -> 41.3672270775 # use stringify_bool
    # -> 46.4586949348 # use stringify_bool and *_identifier

    #from mosql.common import select as old_select

    #print timeit(lambda: old_select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    # -> 67.9556078911
