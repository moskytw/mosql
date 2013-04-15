#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = [
    'escape', 'stringify_bool', 'delimit_identifier', 'escape_identifier',
    'raw', 'default',
    'qualifier', 'value', 'identifier', 'paren',
    'joiner',
    'concat_by_comma', 'concat_by_and', 'concat_by_space', 'concat_by_or',
    'allowed_operators',
    'build_where', 'build_set',
    'Clause', 'Statement',
]

from functools import wraps
from datetime import datetime, date, time

def escape(s):
    '''The function which escapes the value.

    By default, it just replaces ' (single-quote) with '' (two single-quotes).
    '''
    return s.replace("'", "''")

def stringify_bool(b):
    '''The function which stringify the bool.

    By default, it returns ``'TRUE'`` if `b` is true, otherwise it returns
    ``'FALSE'``.
    '''
    return 'TRUE' if b else 'FALSE'

def delimit_identifier(s):
    '''The function which delimits the identifier.

    By default, it conforms the standard to encloses the identifier, `s`, by "
    (double quote).

    .. note::
        MySQL uses ` (back-quote). MS SQL uses [] (brackets).

    Set it ``None`` to disable the feature of delimiting identifiers.
    '''
    return '"%s"' % s

def escape_identifier(s):
    '''The function which escapes the identifier.

    By default, it just replaces " (double-quote) with "" (two double-quotes).
    '''
    return s.replace('"', '""')

class raw(str):
    '''This is a subclass of built-in `str` type. The qualifier function do
    noting when the input is an instance of this class'''

    def __repr__(self):
        return 'raw(%s)' % self

default = raw('DEFAULT')

def _is_iterable_not_str(x):
    return not isinstance(x, basestring) and hasattr(x, '__iter__')

def qualifier(f):
    '''A decorator which makes all items in an `iterable` apply a qualifier
    function, `f`, or simply apply the qualifier function to the input if the
    input is not an `iterable`.

    The `iterable` here means the iterable except string.

    It also makes a qualifier function returns the input without changes if the
    input is an instance of :class:`raw`.
    '''

    @wraps(f)
    def qualifier_wrapper(x):
        if isinstance(x, raw):
            return x
        elif _is_iterable_not_str(x):
            return [item if isinstance(item, raw) else f(item) for item in x]
        else:
            return f(x)

    return qualifier_wrapper

@qualifier
def value(x):
    '''It is a qualifier function for values.

    ================ ======
    input            output
    ================ ======
    string           string escaped (by :func:`escape`)
    datetime objects *same as above*
    `bool`           bool stringified (by :func:`stringify_bool`)
    ``None``         ``'NULL'``
    other            string (by :func:`str`)
    ================ ======
    '''

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
    '''It is a qualifier function for identifiers.

    It uses the :func:`delimit_identifier` and :func:`escape_identifier` to
    qualifiy the input.

    It returns the input with no changes if :func:`delimit_identifier` is
    ``None``.
    '''

    if delimit_identifier is None:
        return s
    else:
        return delimit_identifier(escape_identifier(s))

@qualifier
def paren(s):
    '''A qualifier function which encloses the input with () (paren).'''
    return '(%s)' % s

def joiner(f):
    '''A decorator which makes the input apply this function only if the input
    is an `iterable`, otherwise it just returns the same input.

    The `iterable` here means the iterable except string.
    '''

    @wraps(f)
    def joiner_wrapper(x):
        if _is_iterable_not_str(x):
            return f(x)
        else:
            return x

    return joiner_wrapper

@joiner
def concat_by_and(i):
    '''a joiner function which concats the iterable by ``'AND'``.'''
    return ' AND '.join(i)

@joiner
def concat_by_or(i):
    '''a joiner function which concats the iterable by ``'OR'``.'''
    return ' OR '.join(i)

@joiner
def concat_by_space(i):
    '''a joiner function which concats the iterable by a space.'''
    return ' '.join(i)

@joiner
def concat_by_comma(i):
    '''a joiner function which concats the iterable by , (comma).'''
    return ', '.join(i)

allowed_operators = set([
    '<', '>', '<=', '>=', '=', '<>', '!=',
    'IS', 'IS NOT',
    'IN', 'NOT IN',
    'LIKE', 'NOT LIKE',
    'SIMILAR TO', 'NOT SIMILAR TO',
    '~', '~*', '!~', '!~*',
])
'''The operators which are allowed by :func:`build_where`.

An ``AssertionError`` is raised if an operator not allowed is found.

Set it ``None`` to disable the feature of checking the operator.
'''

def _to_pairs(x):

    if hasattr(x, 'iteritems'):
        x = x.iteritems()
    elif hasattr(x, 'items'):
        x = x.items()

    return x

@joiner
def build_where(x):
    '''It is a joiner function which builds the where list of SQL from a `dict`
    or pairs.'''

    ps = _to_pairs(x)

    pieces = []

    for k, v in ps:

        op = ''

        if not isinstance(k, raw):

            # split the op out
            space_pos = k.find(' ')
            if space_pos != -1:
                k, op = k[:space_pos], k[space_pos+1:].strip()

            # qualify the k and op

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

        # qualify the v
        v = value(v)
        if _is_iterable_not_str(v):
            v = paren(concat_by_comma(v))

        if op:
            pieces.append('%s %s %s' % (k, op, v))
        else:
            pieces.append('%s %s' % (k, v))

    return concat_by_and(pieces)

@joiner
def build_set(x):
    '''It is a joiner function which builds the set list of SQL from a `dict` or
    pairs.'''

    ps = _to_pairs(x)

    pieces = []
    for k, v in ps:
        pieces.append('%s=%s' % (identifier(k), value(v)))

    return concat_by_comma(pieces)

# NOTE: To keep simple, the below classes shouldn't rely on the above functions

class Clause(object):
    '''It represents a clause of SQL.

    :param prefix: the lead word(s) of this clause
    :type prefix: str

    :param formatters: the qualifier or joiner functions
    :type formatters: iterable
    '''

    def __init__(self, prefix, formatters, hidden=False):
        self.prefix = prefix.upper()
        self.formatters = formatters
        self.hidden = hidden

    def format(self, x):
        '''Apply `x` to this clause template.

        :rtype: str
        '''

        for formatter in self.formatters:
            x = formatter(x)

        if self.hidden:
            return '%s' % x
        else:
            return '%s %s' % (self.prefix, x)

    def __repr__(self):
        return 'Clause(%s, %s)' % (self.prefix, self.formatters)

class Statement(object):
    '''It represents a statement of SQL.

    :param clauses: the clauses which consist this statement
    :type clauses: :class:`Clause`
    '''

    def __init__(self, clauses):
        self.clauses = clauses

    def format(self, clause_args):
        '''Apply the `clause_args` to each clauses.

        :param clause_args: the arguments for the clauses
        :type clause_args: dict

        :rtype: str
        '''

        pieces = []
        for clause in self.clauses:
            arg = clause_args.get(clause.prefix.lower().replace(' ', '_'))
            if arg is not None:
                pieces.append(clause.format(arg))
        return ' '.join(pieces)

    def __repr__(self):
        return 'Statement(%s)' % self.clauses

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # insert

    single_identifier = (identifier, )
    identifier_list = (identifier, concat_by_comma)

    insert_into = Clause('insert into', single_identifier)
    columns     = Clause('columns'    , (identifier, concat_by_comma, paren), hidden=True)
    values      = Clause('values'     , (value, concat_by_comma, paren))
    returning   = Clause('returning'  , identifier_list)

    insert_into_stat = Statement([insert_into, columns, values, returning])

    # select

    single_value = (value, )
    where_list  = (build_where, )
    statement_list  = (concat_by_space, )

    select   = Clause('select'  , identifier_list)
    from_    = Clause('from'    , identifier_list)
    joins    = Clause('joins'   , statement_list, hidden=True)
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
    print select('person', {raw("function(x) ="): 'mosky'})

    #print select('person', {"person_id = '' OR true; --": 'mosky'})
    # -> AssertionError: the operator is not allowed: "= '' OR TRUE; --"

    #from timeit import timeit

    #print timeit(lambda: select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    # -> 47.6618270874

    #allowed_operators = None
    #print timeit(lambda: select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    # -> 47.9289941788

    #delimit_identifier = None
    #print timeit(lambda: select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    # -> 43.3604869843

    #from mosql.common import select as old_select

    #print timeit(lambda: old_select('person', {'name': 'Mosky Liu'}, ('person_id', 'name'), limit=10, order_by='person_id'))
    # -> 67.3775911331
