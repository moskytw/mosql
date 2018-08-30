#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides basic bricks to build SQLs.

The five functions below are the core functions of MoSQL and abstract the
variety of SQL specs. You can override them to let MoSQL support non-standard
SQL specs.

.. autosummary::
    escape
    format_param
    stringify_bool
    delimit_identifier
    escape_identifier

.. note::
    There are two built-in patches: :mod:`mosql.mysql` and :mod:`mosql.sqlite`.

They are the subclasses of :class:`str`. You can use them to represent simple
string but having special SQL meaning:

.. autosummary::
    raw
    param

The built-in :class:`raw` instances:

.. autosummary::
    default
    star

The functions which are :func:`qualifier` functions format the Python objects
into SQL strings:

.. autosummary::
    value
    identifier
    identifier_as
    identifier_dir
    paren

The functions which are :func:`joiner` functions concatenate the SQL strings:

.. autosummary::
    concat_by_and
    concat_by_or
    concat_by_space
    concat_by_comma
    build_values_list
    build_where
    build_set
    build_on

The helper functions below fill the gap between the Python objects and SQL:

.. autosummary::
    or_
    and_
    dot
    as_
    asc
    desc
    subq
    in_operand

The main classes let you combine the bricks above to create a final SQL builder:

.. autosummary::
    Clause
    Statement
    Query

.. versionchanged:: 0.1.6
    It is rewritten and totally different from old version.
'''

from __future__ import print_function, unicode_literals

__all__ = [
    'escape', 'format_param', 'stringify_bool',
    'delimit_identifier', 'escape_identifier',
    'raw', 'param', 'default', '___', 'star', 'autoparam',
    'qualifier', 'paren', 'value',
    'DirectionError', 'allowed_directions',
    'identifier', 'identifier_as', 'identifier_dir',
    'joiner',
    'concat_by_comma', 'concat_by_and', 'concat_by_space', 'concat_by_or',
    'OperatorError', 'allowed_operators',
    'build_values_list', 'build_where', 'build_set', 'build_on',
    'or_', 'and_', 'dot', 'as_', 'asc', 'desc', 'subq', 'in_operand',
    'Clause', 'Statement', 'Query'
]

import sys
from datetime import datetime, date, time
from functools import wraps

from . import compat

def warning(s):
    print('Warning: {}'.format(s), file=sys.stderr)

def debug(s):
    print('Debug: {}'.format(s), file=sys.stderr)

def echo(s):
    print(s, file=sys.stderr)

# core functions

def raise_for_null_byte(s):
    if '\x00' in s:
        raise ValueError(
            r'unable to escape \x00. '
            r'It will truncate your SQL, is it an attack?'
        )

def escape(s):
    '''It escapes the value.

    By default, it just replaces ``'`` (single-quote) with ``''`` (two
    single-quotes).

    It aims at avoiding SQL injection. Here are some examples:

    .. doctest::

        >>> tmpl = "select * from person where person_id = '%s';"
        >>> evil_value = "' or true; -- "

        >>> print(tmpl % evil_value)
        select * from person where person_id = '' or true; -- ';

        >>> print(tmpl % escape(evil_value))
        select * from person where person_id = '\'' or true; -- ';

    .. warning ::
        Please use UTF-8 as your connection encoing. Simple escaping will have
        secuirty risk if you use double-byte connection encoding, such as Big5
        or GBK.

    .. versionchanged:: 0.10
        It will raise a ValueError if `s` contains a null byte (``\\x00``).
    '''

    raise_for_null_byte(s)
    return s.replace("'", "''")

std_escape = escape

def format_param(s=''):
    '''It formats the parameter of prepared statement.

    By default, it formats the parameter in `pyformat
    <http://www.python.org/dev/peps/pep-0249/#paramstyle>`_.

    >>> print(format_param('name'))
    %(name)s

    >>> print(format_param())
    %s
    '''
    return '%%(%s)s' % s if s else '%s'

std_format_param = format_param

def stringify_bool(b):
    '''It stringifies the bool.

    By default, it returns ``TRUE`` if `b` is true, otherwise it returns
    ``FALSE``.
    '''
    return 'TRUE' if b else 'FALSE'

std_stringify_bool = stringify_bool

def delimit_identifier(s):
    '''It delimits the identifier.

    By default, it conforms the standard to encloses the identifier, `s`, by
    ``"`` (double quote).

    .. versionchanged:: 0.10
        It's not disableable anymore. Use :class:`raw` instead.
    '''
    return '"%s"' % s

std_delimit_identifier = delimit_identifier

def escape_identifier(s):
    r'''It escapes the identifier.

    By default, it just replaces ``"`` (double-quote) with ``""`` (two
    double-quotes).

    It also aims at avoid SQL injection. Here are some examples:

    .. doctest::

        >>> tmpl = 'select * from person where "%s" = \'mosky\';'
        >>> evil_identifier = 'person_id" = \'\' or true; -- '

        >>> print(tmpl % evil_identifier)
        select * from person where "person_id" = '' or true; -- " = 'mosky';

        >>> print(tmpl % escape_identifier(evil_identifier))
        select * from person where "person_id"" = '' or true; -- " = 'mosky';

    .. warning ::
        Please use UTF-8 as your connection encoing. Simple escaping will have
        secuirty risk if you use double-byte connection encoding, such as Big5
        or GBK.

    .. versionchanged:: 0.10
        It will raise a ValueError if `s` contains a null byte (``\x00``).
    '''

    raise_for_null_byte(s)
    return s.replace('"', '""')

std_escape_identifier = escape_identifier

# special str subclass

class raw(compat.text_type):
    '''The qualifier functions do nothing when the input is an instance of this
    class. This is a subclass of the built-in text type.

    .. warning ::
        It's your responsibility to ensure the security when you use
        :class:`raw` string.
    '''

    def __repr__(self):
        return str('raw(%s)' % super(raw, self).__repr__())

default = raw('DEFAULT')
'The ``DEFAULT`` keyword in SQL.'

star = raw('*')
'The ``*`` keyword in SQL.'

class param(compat.text_type):
    '''The :func:`value` builds this type as a parameter for the prepared
    statement.

    >>> print(value(param('')))
    %s
    >>> print(value(param('name')))
    %(name)s

    This is a subclass of the built-in text type.

    The :class:`___` is an alias of it.
    '''

    def __repr__(self):
        return str('param(%s)' % super(param, self).__repr__())

___ = autoparam = object()
'''A special token that is converted to a parameter automatically by
:func:`value` in a prepared statement.'''

# qualifier functions

if compat.PY2:
    def _is_iterable_not_str(x):
        return hasattr(x, '__iter__')

    def _coerce_str(x):
        if isinstance(x, compat.binary_type):
            x = x.decode('utf-8')
        return x

    def _qualifier(f):
        @wraps(f)
        def qualifier_wrapper(x):
            if isinstance(x, raw):
                return x
            elif _is_iterable_not_str(x):
                return [
                    item if isinstance(item, raw) else f(_coerce_str(item))
                    for item in x
                ]
            else:
                return f(_coerce_str(x))

        return qualifier_wrapper
else:
    def _is_iterable_not_str(x):
        return not isinstance(x, (str, bytes,)) and hasattr(x, '__iter__')

    def _qualifier(f):
        @wraps(f)
        def qualifier_wrapper(x):
            if isinstance(x, raw):
                return x
            elif _is_iterable_not_str(x):
                return [
                    item if isinstance(item, raw) else f(item)
                    for item in x
                ]
            else:
                return f(x)

        return qualifier_wrapper

qualifier = _qualifier
'''A decorator which makes all items in an `iterable` apply a qualifier
function, `f`, or simply apply the qualifier function to the input if the input
is not an `iterable`.

The `iterable` here means the iterable except string.

It also makes a qualifier function returns the input without changes if the
input is an instance of :class:`raw`.
'''

@qualifier
def value(x):
    '''A qualifier function which formats Python object as SQL value.

    >>> print(value('normal string'))
    'normal string'

    >>> print(value(u'normal unicode'))
    'normal unicode'

    >>> print(value(True))
    TRUE

    >>> print(value(datetime(2013, 4, 19, 14, 41, 10)))
    '2013-04-19 14:41:10'

    >>> print(value(date(2013, 4, 19)))
    '2013-04-19'

    >>> print(value(time(14, 41, 10)))
    '14:41:10'

    >>> print(value(raw('count(person_id) > 1')))
    count(person_id) > 1

    >>> print(value(param('myparam')))
    %(myparam)s
    '''

    # 1. raw and 2. param are subclasses of str, so the two types must be
    # first than str.

    if x is None:
        return 'NULL'
    elif isinstance(x, param):
        return format_param(x)
    elif isinstance(x, compat.string_types):
        return "'%s'" % escape(x)
    elif isinstance(x, (datetime, date, time)):
        return "'%s'" % x
    elif isinstance(x, bool):
        return stringify_bool(x)
    else:
        # TODO: int goes here, but it will be better to handle explicitly
        return compat.text_type(x)

class DirectionError(Exception):
    '''The instance of it will be raised when :func:`identifier` detects an
    invalid direction.

    .. seealso ::
        The operators allowed --- :attr:`allowed_directions`.'''

    def __init__(self, op):
        self.op = op

    def __str__(self):
        return "this direction is not allowed: '%s'" % compat.text_type(self.op)

allowed_directions = set(['DESC', 'ASC'])
'''The directions which are allowed by :func:`identifier_dir`.

A :exc:`DirectionError` will be raised if a direction not allowed is found.

.. versionchanged:: 0.10
    It's not disableable anymore. Use :class:`raw` instead.
'''

def _is_pair(x):
    return _is_iterable_not_str(x) and len(x) == 2

@qualifier
def identifier(s):
    '''A qualifier function which formats Python object as SQL identifier.

    It uses the :func:`delimit_identifier` and :func:`escape_identifier` to
    qualify the input.

    >>> print(identifier('column_name'))
    "column_name"

    >>> print(identifier('table_name.column_name'))
    "table_name"."column_name"

    It also supports to use pair in pair-list format.

    >>> print(identifier([('table_name', 'column_name')])[0])
    "table_name"."column_name"

    .. versionchanged:: 0.10
        Support to use pair-list to represent dot.

    .. versionchanged:: 0.10
        It doesn't support ``AS`` and order directon anymore. Use
        :func:`identifier_as` or :func:`identifier_dir` instead.

    .. seealso ::
        There is also a :func:`dot` function.
    '''

    # t: table name
    # c: column name
    t = ''
    c = ''

    if _is_pair(s):
        t, c = s
    else:
        t, _, c = s.rpartition('.')

    if not t:
        return delimit_identifier(escape_identifier(c))
    else:
        return (
            delimit_identifier(escape_identifier(t)) +
            '.' +
            delimit_identifier(escape_identifier(c))
        )

@qualifier
def identifier_as(s):
    '''A qualifier function which formats Python object as SQL identifiers with
    ``AS``.

    >>> print(identifier_as('column_name as c'))
    "column_name" AS "c"

    >>> print(identifier_as('table_name.column_name as c'))
    "table_name"."column_name" AS "c"

    It also supports to use pair in pair-list format. It is a qualifier
    function, so you have to put the pair in another list.

    >>> print(identifier_as([('table_name.column_name', 'c')])[0])
    "table_name"."column_name" AS "c"

    >>> print(identifier_as([(raw('count(table_name.column_name)'), 'c')])[0])
    count(table_name.column_name) AS "c"

    It uses :func:`identifier` to build normal identifier string without ``AS``.

    >>> print(identifier_as('column_name'))
    "column_name"

    >>> print(identifier_as('table_name.column_name'))
    "table_name"."column_name"

    .. seealso ::
        There is also an :func:`as_` function.

    .. versionadded:: 0.10
    '''

    # i: identifier part
    # a: alias name
    i = ''
    a = ''

    if _is_pair(s):
        i, a = s
    else:
        i, _, a = s.partition(' as ')
        if not a:
            i, _, a = s.partition(' AS ')

    if not a:
        return identifier(i)
    else:
        return (
            identifier(i) +
            ' AS ' +
            delimit_identifier(escape_identifier(a))
        )

@qualifier
def identifier_dir(s):
    '''A qualifier function which formats Python object as SQL identifiers with
    order direction.

    >>> print(identifier_dir('table_name ASC'))
    "table_name" ASC

    >>> print(identifier_dir('table_name.column_name DESC'))
    "table_name"."column_name" DESC

    It also supports to use pair in pair-list format. It is a qualifier
    function, so you have to put the pair in another list.

    >>> print(identifier_dir([('table_name.column_name', 'ASC')])[0])
    "table_name"."column_name" ASC

    >>> print(identifier_dir([(raw('count(table_name.column_name)'), 'DESC')])[0])
    count(table_name.column_name) DESC

    It uses :func:`identifier` to build normal identifier string without order direction.

    >>> print(identifier_dir('column_name'))
    "column_name"

    >>> print(identifier_dir('table_name.column_name'))
    "table_name"."column_name"

    .. seealso ::
        There are also :func:`asc` and :func:`desc` functions.

    .. versionadded:: 0.10
    '''

    # i: identifier part
    # d: direction
    i = ''
    d = ''

    if _is_pair(s):
        i, d = s
    else:
        i, _, d = s.partition(' ')

    if not d:
        return identifier(s)
    else:
        # PostgreSQL supports ``USING operator``, ``NULLS FIRST``, ...
        if not isinstance(d, raw):
            d = d.upper()
            if d not in allowed_directions:
                raise DirectionError(d)
        return identifier(i) + ' ' + d

@qualifier
def paren(s):
    '''A qualifier function which encloses the input with ``()`` (paren).'''
    return '(%s)' % s

# joiner functions

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
    '''A joiner function which concats the iterable by ``'AND'``.'''
    return ' AND '.join(i)

@joiner
def concat_by_or(i):
    '''A joiner function which concats the iterable by ``'OR'``.'''
    return ' OR '.join(i)

@joiner
def concat_by_space(i):
    '''A joiner function which concats the iterable by a space.'''
    return ' '.join(i)

@joiner
def concat_by_comma(i):
    '''A joiner function which concats the iterable by ``,`` (comma).'''
    return ', '.join(i)

class OperatorError(Exception):
    '''The instance of it will be raised when :func:`build_where` detects an
    invalid operator.

    .. seealso ::
        The operators allowed --- :attr:`allowed_operators`.'''

    def __init__(self, op):
        self.op = op

    def __str__(self):
        return 'this operator is not allowed: "%s"' % compat.text_type(self.op)

allowed_operators = set([
    '<', '>', '<=', '>=', '=', '<>', '!=',
    'IS', 'IS NOT',
    'IN', 'NOT IN',
    'LIKE', 'NOT LIKE',
    'SIMILAR TO', 'NOT SIMILAR TO',
    '~', '~*', '!~', '!~*',
])
'''The operators which are allowed by :func:`build_where`.

An :exc:`OperatorError` will be raised if an operator not allowed is found.

.. versionchanged:: 0.10
    It's not disableable anymore. Use :class:`raw` instead.
'''

@joiner
def build_values_list(x):
    '''A joiner function which builds the values-list for ``VALUES`` clause.

    The `x` can be either

    1. iterable values; or
    2. iterable values in another iterable.

    .. versionadded:: 0.10
    '''

    if hasattr(x, '__getitem__') and _is_iterable_not_str(x[0]):
        return concat_by_comma(paren(
            concat_by_comma(value(item))
        ) for item in x)

    return paren(concat_by_comma(value(x)))

def _to_pairs(x):

    if hasattr(x, 'iteritems'):
        x = x.iteritems()
    elif hasattr(x, 'items'):
        x = x.items()

    return x

def _build_condition(x, key_qualifier=identifier, value_qualifier=value):

    ps = _to_pairs(x)

    pieces = []

    for k, v in ps:

        # find the op

        op = ''

        # TODO: let user use subquery with operator in first (key) part
        # if k is raw, it means we can't modify the k and op
        if not isinstance(k, raw):
            if _is_pair(k):
                # unpack the op out
                k, op = k

            if not op:
                # split the op out
                k, _, op = k.partition(' ')

            if not op:
                # decide op automatically
                if _is_iterable_not_str(v):
                    op = 'IN'
                elif v is None:
                    op = 'IS'
                else:
                    op = '='

            if not isinstance(op, raw):
                # normalize the op
                op = op.strip().upper()
                # verify the op
                if op not in allowed_operators:
                    raise OperatorError(op)

        # feature of autoparam
        if v is autoparam:
            v = param(k)

        # qualify the k
        k = key_qualifier(k)

        # qualify the v
        v = value_qualifier(v)
        if _is_iterable_not_str(v):
            v = paren(concat_by_comma(v))

        if op == 'IN' and v == '()':
            pieces.append(stringify_bool(False))
        elif op:
            pieces.append('%s %s %s' % (k, op, v))
        else:
            pieces.append('%s %s' % (k, v))

    return concat_by_and(pieces)

@joiner
def build_where(x):
    r'''A joiner function which builds the where-list of SQL from a `dict` or
    `pairs`.

    The `x` can be a `dict` or `pairs`:

    >>> print(build_where({'detail_id': 1, 'age >= ': 20, 'created': date(2013, 4, 16)}))  # doctest: +SKIP
    "created" = '2013-04-16' AND "detail_id" = 1 AND "age" >= 20

    >>> print(build_where((('detail_id', 1), ('age >= ', 20), ('created', date(2013, 4, 16)))))
    "detail_id" = 1 AND "age" >= 20 AND "created" = '2013-04-16'

    The key can be a `pair` to include an operator::

        >>> print(build_where({'detail_id': 1, ('age', '>='): 20, 'created': date(2013, 4, 16)}))
        "age" >= 20 AND "detail_id" = 1 AND "created" = '2013-04-16'

    The default operator will be decided by the value.

    >>> print(build_where({'name': None}))
    "name" IS NULL

    >>> print(build_where({'person_id': ['andy', 'bob']}))
    "person_id" IN ('andy', 'bob')

    >>> print(build_where({'person_id': []}))
    FALSE

    .. seealso ::
        There are also :func:`subq` and :func:`in_operand` functions.

    It supports all common operators, such as ``LIKE``:

    >>> print(build_where({'email like': '%@gmail.com%'}))
    "email" LIKE '%@gmail.com%'

    .. seealso ::
        By default, the operators are limited. Check the
        :attr:`allowed_operators` for more information.

    If need, wrap key with :func:`raw` to use function:

    >>> print(build_where({raw('count(person_id) >'): 10}))
    count(person_id) > 10

    Build prepared where::

        >>> print(build_where({'custom_param': param('my_param'), 'auto_param': param, 'using_alias': ___}))
        "auto_param" = %(auto_param)s AND "using_alias" = %(using_alias)s AND "custom_param" = %(my_param)s

    It does nothing if `x` is a string:

    >>> print(build_where('"detail_id" = 1 AND "age" >= 20 AND "created" = \'2013-04-16\''))
    "detail_id" = 1 AND "age" >= 20 AND "created" = '2013-04-16'

    .. versionchanged:: 0.10
        Supports to use `pair` key to include operator.

    .. versionchanged:: 0.10
        If the value is empty iterable, it translates it into ``FALSE`` rather
        than ``x IN ()`` which caused syntax error in SQL.
    '''
    return _build_condition(x, identifier, value)

@joiner
def build_set(x):
    r'''A joiner function which builds the set-list of SQL from a `dict` or
    pairs.

    The `x` can be a `dict` or `pairs`:

    >>> print(build_set({'a': 1, 'b': True, 'c': date(2013, 4, 16)}))  # doctest: +SKIP
    "a"=1, "c"='2013-04-16', "b"=TRUE

    >>> print(build_set((('a', 1), ('b', True), ('c', date(2013, 4, 16)))))
    "a"=1, "b"=TRUE, "c"='2013-04-16'

    Building prepared set::

        >>> print(build_set({'custom_param': param('myparam'), 'auto_param': param}))
        "auto_param"=%(auto_param)s, "custom_param"=%(myparam)s

    It does nothing if `x` is a string:

    >>> print(build_set('"a"=1, "b"=TRUE, "c"=\'2013-04-16\''))
    "a"=1, "b"=TRUE, "c"='2013-04-16'
    '''

    ps = _to_pairs(x)

    pieces = []
    for k, v in ps:

        # feature of autoparam
        if v is autoparam:
            v = param(k)

        pieces.append('%s=%s' % (identifier(k), value(v)))

    return concat_by_comma(pieces)

@joiner
def build_on(x):
    '''A joiner function which builds the on-list of SQL from a `dict` or pairs.
    The difference from :func:`build_where` is the value here will be treated as
    an identifier.

    >>> print(build_on({'person_id': 'friend_id'}))
    "person_id" = "friend_id"

    >>> print(build_on((('person.person_id', 'detail.person_id'), )))
    "person"."person_id" = "detail"."person_id"

    >>> print(build_on({'person.age >': raw(20)}))
    "person"."age" > 20
    '''
    return _build_condition(x, identifier, identifier)

# helper functions

def or_(conditions):
    '''It concats the conditions by ``OR``.

    >>> print(or_(({'person_id': 'andy'}, {'person_id': 'bob'})))
    ("person_id" = 'andy') OR ("person_id" = 'bob')

    .. versionchanged:: 0.7.2
        It helps you to add parens now.

    .. versionadded:: 0.6
    '''

    return concat_by_or(paren(build_where(c)) for c in conditions)

def and_(conditions):
    '''It concats the conditions by ``AND``.

    >>> print(and_(({'person_id': 'andy'}, {'name': 'Andy'})))
    ("person_id" = 'andy') AND ("name" = 'Andy')

    .. versionadded:: 0.7.3
    '''

    return concat_by_and(paren(build_where(c)) for c in conditions)

def dot(s, t):
    '''It treats `s` and `t` as identifiers, concats them by ``.``, and then
    makes the whole string as :class:`raw`.

    >>> print(dot('table', 'column'))
    "table"."column"

    .. versionadded:: 0.10
    '''
    return raw('{}.{}'.format(identifier(s), identifier(t)))

def as_(s, t):
    '''It treats `s` and `t` as identifiers, concats them by ``AS``, and then
    makes the whole string as :class:`raw`.

    >>> print(as_('column', 'c'))
    "column" AS "c"

    >>> print(as_('table.column', 'c'))
    "table"."column" AS "c"

    .. versionadded:: 0.10
    '''
    return raw('{} AS {}'.format(identifier(s), identifier(t)))

def asc(s):
    '''It treats `s` as an identifier, adds ``ASC`` after `s`, and then makes
    the whole string as :class:`raw`.

    >>> print(asc('score'))
    "score" ASC

    .. versionadded:: 0.10
    '''
    return raw('{} ASC'.format(identifier(s)))

def desc(s):
    '''It treats `s` as an identifier, adds ``DESC`` after `s`, and then makes
    the whole string as :class:`raw`.

    >>> print(desc('score'))
    "score" DESC

    .. versionadded:: 0.10
    '''
    return raw('{} DESC'.format(identifier(s)))

def subq(s):
    '''It adds parens and makes `s` as :class:`raw`.

    >>> print(subq("select person_id from person where join_ts >= '2014-11-27'"))
    (select person_id from person where join_ts >= '2014-11-27')

    .. versionadded:: 0.10
    '''
    return raw(paren(s))

def in_operand(x):
    '''It stringifies `x` as an right operand for ``IN``.

    >>> print(in_operand(['a', 'b', 'c']))
    ('a', 'b', 'c')

    If you use MoSQL's :class:`Query`, please just put `x` as value. This
    function is designed for the case which doesn't use MoSQL's :class:`Query`.

    .. versionadded:: 0.10
    '''

    if not _is_iterable_not_str(x):
        x = (x, )

    return paren(concat_by_comma(value(x)))

# NOTE: To keep simple, the below classes shouldn't rely on the above functions

class Clause(object):
    '''It represents a clause of SQL.

    :param prefix: the lead word(s) of this clause
    :type prefix: str
    :param formatters: the qualifier or joiner functions
    :type formatters: sequence
    :param hidden: it decides the prefix will be hidden or not
    :type hidden: bool
    :param alias: another name of this clause
    :type alias: str
    :param default: it will be used if you pass ``None`` to :meth:`format`
    :type default: str
    :param no_argument: set ``True`` if this clause doesn't have any argument
    :type no_argument: bool

    Here is an example of using :class:`Clause`:

    >>> values = Clause('values', (value, concat_by_comma, paren))

    >>> print(values.format(('a', 'b', 'c')))
    VALUES ('a', 'b', 'c')

    >>> print(values.format((default, 'b', 'c')))
    VALUES (DEFAULT, 'b', 'c')

    >>> print(values.format((raw('r'), 'b', 'c')))
    VALUES (r, 'b', 'c')

    .. versionchanged:: 0.9
        Added `no_argument` and made `formatters` has default.

    .. versionchanged:: 0.6
        Added two arguments, `alias` and `default`.
    '''

    def __init__(self, name, formatters=tuple(), hidden=False, alias=None, default=None, no_argument=False):

        self.prefix = name.upper()
        self.formatters = formatters
        self.hidden = hidden
        self.no_argument = no_argument

        # the default and possibles both are used by Statement
        self.default = default
        self.possibles = []

        if alias:
            self.possibles.append(alias)

        lower_name = name.lower()
        underscore_lower_name = lower_name.replace(' ', '_')
        self.possibles.append(underscore_lower_name)

        if lower_name != underscore_lower_name:
            self.possibles.append(lower_name)

    def format(self, x):
        '''Apply `x` to this clause template.

        :rtype: str
        '''

        if self.no_argument and x:
            return self.prefix

        for formatter in self.formatters:
            x = formatter(x)

        if _is_iterable_not_str(x):
            x = ''.join(x)

        if self.hidden:
            return '%s' % x
        else:
            return '%s %s' % (self.prefix, x)

    def __repr__(self):
        return 'Clause(%r, %r)' % (self.prefix, self.formatters)

class Statement(object):
    '''It represents a statement of SQL.

    :param clauses: the clauses which consist this statement
    :type clauses: :class:`Clause`
    :param preprocessor: a preprocessor for the argument, `clause_args`, of the :meth:`format`
    :type preprocessor: function

    Here is an example of using :class:`Statement`:

    >>> insert_into = Clause('insert into', (identifier, ))
    >>> columns     = Clause('columns'    , (identifier, concat_by_comma, paren), hidden=True)
    >>> values      = Clause('values'     , (value, concat_by_comma, paren))

    >>> insert_into_stat = Statement((insert_into, columns, values))

    >>> print(insert_into_stat.format({
    ...     'insert into': 'person',
    ...     'columns'    : ('person_id', 'name'),
    ...     'values'     : ('daniel', 'Diane Leonard'),
    ... }))
    INSERT INTO "person" ("person_id", "name") VALUES ('daniel', 'Diane Leonard')

    .. versionchanged:: 0.6
        Added `preprocessor`.
    '''

    def __init__(self, clauses, preprocessor=None):
        self.clauses = clauses
        self.preprocessor = preprocessor

    def format(self, clause_args):
        '''Apply the `clause_args` to each clauses.

        :param clause_args: the arguments for the clauses
        :type clause_args: dict

        :rtype: str

        .. versionchanged:: 0.10
            Now it raises `TypeError` if there is any unused clause argument.

        .. versionchanged:: 0.10
            Now if an argument's value is false in boolean context, it will
            ignore that argument.
        '''

        if self.preprocessor:
            clause_args = clause_args.copy()
            self.preprocessor(clause_args)

        # it is for checking unused clause args
        # e.g., select(wehere={})
        # ca: clause_args
        unused_ca_count = len(clause_args)

        pieces = []
        for clause in self.clauses:

            # find the arg for this clause
            arg = None
            for possible in clause.possibles:
                if possible in clause_args:
                    arg = clause_args[possible]
                    unused_ca_count -= 1
                    break

            # if not found and have default, use default
            if arg is None and clause.default:
                arg = clause.default

            # if not found or len(arg) == 0
            if arg:
                pieces.append(clause.format(arg))

        if unused_ca_count:
            all_possibles = set(
                p
                for clause in self.clauses
                for p in clause.possibles
            )
            raise TypeError('unused clause args: {}'.format(', '.join(
                k
                for k in clause_args
                if k not in all_possibles
            )))

        return ' '.join(pieces)

    def __repr__(self):
        return 'Statement(%r)' % self.clauses

def _merge_dicts(default, *updates):
    result = default.copy()
    for update in updates:
        result.update(update)
    return result

class Query(object):
    '''It makes :class:`Statement` callable and partializeable.

    :param statement: a statement
    :type statement: :class:`Statement`
    :param positional_keys: the positional arguments accepted by :meth:`stringify`.
    :type positional_keys: sequence
    :param clause_args: the arguments of the clauses you want to predefine
    :type clause_args: dict

    You can use a :class:`Query` instance like a function:

    >>> from mosql.query import insert
    >>> print(insert)
    insert(table=None, set=None, *, insert_into=None, columns=None, values=None, returning=None, on_duplicate_key_update=None)

    .. versionadded:: 0.6
    '''

    def __init__(self, statement, positional_keys=None, clause_args=None):

        self.statement = statement
        self.positional_keys = positional_keys

        if clause_args is None:
            self.clause_args = {}
        else:
            self.clause_args = clause_args

    def breed(self, clause_args=None):
        '''It merges the `clause_args` from both this instance and the argument,
        and then create new :class:`Query` instance by that.'''
        return Query(
            self.statement,
            self.positional_keys,
            _merge_dicts(self.clause_args, clause_args)
        )

    def format(self, clause_args=None):
        '''It merges the `clause_args` from both this instance and the
        arguments, and then apply to the statement.'''
        clause_args = _merge_dicts(self.clause_args, clause_args)
        return self.statement.format(clause_args)

    def stringify(self, *positional_values, **clause_args):
        '''It is same as the :meth:`format`, but the parameters are more like a
        function.

        A :class:`Query` instance is callable. When you call it, it uses this
        method to handle.
        '''

        if self.positional_keys and positional_values:
            for k, v in zip(self.positional_keys, positional_values):
                clause_args.setdefault(k, v)

        return self.format(clause_args)

    def __call__(self, *positional_values, **clause_args):
        '''It is same as the :meth:`stringify`.'''
        return self.stringify(*positional_values, **clause_args)

    def __repr__(self):
        return 'Query(%r, %r, %r)' % (self.statement, self.positional_keys, self.clause_args)

    def __str__(self):
        return '{}({}, *, {})'.format(
            self.statement.clauses[0].prefix.partition(' ')[0].lower(),
            ', '.join(
                '{}=None'.format(k)
                for k in self.positional_keys
            ), ', '.join(
                '{}=None'.format(clause.prefix.lower().replace(' ', '_'))
                for clause in self.statement.clauses
            )
        )

    _format = format

    def _format_n_echo(self, clause_args=None):
        sql = self._format(clause_args)
        echo(sql)
        return sql

    def enable_echo(self):
        '''Enables echo.

        .. versionadded:: 0.10'''
        self.format = self._format_n_echo

    def disable_echo(self):
        '''Disables echo.

        .. versionadded:: 0.10'''
        self.format = self._format

if __name__ == '__main__':
    import doctest
    doctest.testmod()
