#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides the basic bricks to build SQLs.

The classes or functions you may use frequently:

.. autosummary ::
    raw
    default
    star
    param
    or_
    and_
    subq

It is designed for standard SQL and tested in PostgreSQL. If your database uses
non-standard SQL, such as MySQL, you may need to customize and override the
following functions.

.. autosummary ::
    escape
    format_param
    stringify_bool
    delimit_identifier
    escape_identifier

.. note::

    For MySQL, an official patch is here - :doc:`/mysql`.

If you need to customize more, the following classes may help you.

.. autosummary ::
    Clause
    Statement
    Query

.. versionchanged:: 0.1.6
    It is rewritten and totally different from old version.
'''

__all__ = [
    'escape', 'format_param', 'stringify_bool',
    'delimit_identifier', 'escape_identifier',
    'raw', 'param', 'default', '___', 'star',
    'qualifier', 'paren', 'value',
    'OptionError', 'allowed_options', 'identifier', 'identifier_as', 'identifier_dir',
    'joiner',
    'concat_by_comma', 'concat_by_and', 'concat_by_space', 'concat_by_or',
    'OperatorError', 'allowed_operators',
    'build_values_list', 'build_where', 'build_set', 'build_on',
    'or_', 'and_', 'dot', 'as_', 'asc', 'desc', 'in_operand', 'subq',
    'Clause', 'Statement', 'Query'
]

import sys
if sys.version_info >= (3,):
    unicode = str
    basestring = str

from functools import wraps
from datetime import datetime, date, time

def warning(s):
    print >> sys.stderr, 'Warning: {}'.format(s)

def debug(s):
    print >> sys.stderr, 'Debug: {}'.format(s)

# lowest-level

def escape(s):
    '''It escapes the value.

    By default, it just replaces ``'`` (single-quote) with ``''`` (two single-quotes).

    It aims at avoiding SQL injection. Here are some examples:

    >>> tmpl = "select * from person where person_id = '%s';"
    >>> evil_value = "' or true; -- "

    >>> print tmpl % evil_value
    select * from person where person_id = '' or true; -- ';

    >>> print tmpl % escape(evil_value)
    select * from person where person_id = '\'' or true; -- ';

    .. warning ::
        If you don't use utf-8 for your connection, such as big5, gbk, please
        use native escape function to ensure the security. See
        :mod:`mosql.psycopg2_escape` or :mod:`mosql.MySQLdb_escape` for more
        information.

    .. versionchanged:: 0.9.2
        It will raise a ValueError if `s` contains a null byte (\\x00).
    '''

    if s.find('\x00') != -1:
        raise ValueError(
            r'unable to escape \x00. '
            r'It will truncate your SQL, is it an attack?'
        )

    return s.replace("'", "''")

std_escape = escape

def format_param(s=''):
    '''It formats the parameter of prepared statement.

    By default, it formats the parameter in `pyformat
    <http://www.python.org/dev/peps/pep-0249/#paramstyle>`_.

    >>> format_param('name')
    '%(name)s'

    >>> format_param()
    '%s'
    '''
    return '%%(%s)s' % s if s else '%s'

std_format_param = format_param

def stringify_bool(b):
    '''It stringifies the bool.

    By default, it returns ``'TRUE'`` if `b` is true, otherwise it returns
    ``'FALSE'``.
    '''
    return 'TRUE' if b else 'FALSE'

std_stringify_bool = stringify_bool

def delimit_identifier(s):
    '''It delimits the identifier.

    By default, it conforms the standard to encloses the identifier, `s`, by
    ``"`` (double quote).

    .. versionchanged:: 0.9.2
        It's not disableable anymore. Use :class:`raw` instead.
    '''
    return '"%s"' % s

std_delimit_identifier = delimit_identifier

def escape_identifier(s):
    r'''It escapes the identifier.

    By default, it just replaces ``"`` (double-quote) with ``""`` (two double-quotes).

    It also aims at avoid SQL injection. Here are some examples:

    >>> tmpl = 'select * from person where "%s" = \'mosky\';'
    >>> evil_identifier = 'person_id" = \'\' or true; -- '

    >>> print tmpl % evil_identifier
    select * from person where "person_id" = '' or true; -- " = 'mosky';

    >>> print tmpl % escape_identifier(evil_identifier)
    select * from person where "person_id"" = '' or true; -- " = 'mosky';
    '''
    return s.replace('"', '""')

std_escape_identifier = escape_identifier

class raw(str):
    '''The qualifier function does nothing when the input is an instance of this
    class. This is a subclass of built-in `str` type.

    .. warning ::
        It is your responsibility to ensure that your SQL queries are properly escaped if you use this class.
    '''

    def __repr__(self):
        return 'raw(%r)' % str(self)

default = raw('DEFAULT')
'The ``DEFAULT`` keyword in SQL.'

star = raw('*')
'The ``*`` keyword in SQL.'

class param(str):
    '''The :func:`value` builds this type as a parameter for the prepared statement.

    >>> value(param(''))
    '%s'
    >>> value(param('name'))
    '%(name)s'

    This is just a subclass of built-in `str` type.

    The :class:`___` is an alias of it.
    '''

    def __repr__(self):
        return 'param(%r)' % self

___ = param

# low-level

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
            if isinstance(x, unicode):
                x = x.encode('utf-8')
            return f(x)

    return qualifier_wrapper

@qualifier
def value(x):
    '''A qualifier function for values.

    >>> print value('normal string')
    'normal string'

    >>> print value(u'normal unicode')
    'normal unicode'

    >>> print value(True)
    TRUE

    >>> print value(datetime(2013, 4, 19, 14, 41, 10))
    '2013-04-19 14:41:10'

    >>> print value(date(2013, 4, 19))
    '2013-04-19'

    >>> print value(time(14, 41, 10))
    '14:41:10'

    >>> print value(raw('count(person_id) > 1'))
    count(person_id) > 1

    >>> print value(param('myparam'))
    %(myparam)s
    '''

    # NOTE: 1. raw and 2. param are subclasses of str, so the two types must be
    # first than str.

    if x is None:
        return 'NULL'
    elif isinstance(x, param):
        return format_param(x)
    elif isinstance(x, basestring):
        return "'%s'" % escape(x)
    elif isinstance(x, (datetime, date, time)):
        return "'%s'" % x
    elif isinstance(x, bool):
        return stringify_bool(x)
    else:
        return str(x)

class OptionError(Exception):
    '''The instance of it will be raised when :func:`identifier` detects an
    invalid option.

    .. seealso ::
        The operators allowed --- :attr:`allowed_options`.'''

    def __init__(self, op):
        self.op = op

    def __str__(self):
        return 'this option is not allowed: %r' % self.op

allowed_options = set(['DESC', 'ASC'])
'''The options which are allowed by :func:`identifier`.

An :exc:`OptionError` is raised if an option not allowed is found.

.. versionchanged:: 0.9.2
    It's not disableable anymore. Use :class:`raw` instead.
'''

def _is_pair(x):
    return _is_iterable_not_str(x) and len(x) == 2

@qualifier
def identifier(s):
    '''A qualifier function for identifiers.

    It uses the :func:`delimit_identifier` and :func:`escape_identifier` to
    qualify the input.

    >>> print identifier('column_name')
    "column_name"

    >>> print identifier('table_name.column_name')
    "table_name"."column_name"

    It also supports to use pair in pair-list format.

    >>> print identifier([('table_name', 'column_name')])[0]
    "table_name"."column_name"

    .. versionchanged:: 0.9.2
        Support to use pair-list to represent dot.

    .. versionchanged:: 0.9.2
        It doesn't support ``as`` and order directon anymore. Use
        :func:`identifier_as` or :func:`identifier_dir` instead.
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
            delimit_identifier(escape_identifier(t))+
            '.'+
            delimit_identifier(escape_identifier(c))
        )

@qualifier
def identifier_as(s):
    '''A qualifier function for identifiers with ``as``.

    >>> print identifier_as('column_name as c')
    "column_name" AS "c"

    >>> print identifier_as('table_name.column_name as c')
    "table_name"."column_name" AS "c"

    It also supports to use pair in pair-list format.

    >>> print identifier_as([('table_name.column_name', 'c')])[0]
    "table_name"."column_name" AS "c"

    >>> print identifier_as([(raw('count(table_name.column_name)'), 'c')])[0]
    count(table_name.column_name) AS "c"

    It builds a normal identifier string without ``as``.

    >>> print identifier_as('column_name')
    "column_name"

    >>> print identifier_as('table_name.column_name')
    "table_name"."column_name"

    ..versionadded :: 0.9.2
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
            identifier(i)+
            ' AS '+
            delimit_identifier(escape_identifier(a))
        )

@qualifier
def identifier_dir(s):
    '''A qualifier function for identifiers with order direction.

    >>> print identifier_dir('table_name ASC')
    "table_name" ASC

    >>> print identifier_dir('table_name.column_name DESC')
    "table_name"."column_name" DESC

    >>> print identifier_dir([('table_name.column_name', 'ASC')])[0]
    "table_name"."column_name" ASC

    >>> print identifier_dir([(raw('count(table_name.column_name)'), 'DESC')])[0]
    count(table_name.column_name) DESC

    It builds a normal identifier string without order direction.

    >>> print identifier_dir('column_name')
    "column_name"

    >>> print identifier_dir('table_name.column_name')
    "table_name"."column_name"

    ..versionadded :: 0.9.2
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
            if d not in allowed_options:
                raise OptionError(d)
        return identifier(i)+ ' '+d

@qualifier
def paren(s):
    '''A qualifier function which encloses the input with ``()`` (paren).'''
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
        return 'this operator is not allowed: %r' % self.op

allowed_operators = set([
    '<', '>', '<=', '>=', '=', '<>', '!=',
    'IS', 'IS NOT',
    'IN', 'NOT IN',
    'LIKE', 'NOT LIKE',
    'SIMILAR TO', 'NOT SIMILAR TO',
    '~', '~*', '!~', '!~*',
])
'''The operators which are allowed by :func:`build_where`.

An :exc:`OperatorError` is raised if an operator not allowed is found.

.. versionchanged:: 0.9.2
    It's not disableable anymore. Use :class:`raw` instead.
'''

@joiner
def build_values_list(x):
    '''It builds the values list for ``VALUES`` clause.

    The `x` can be either

    1. iterable values; or
    2. iterable values in another iterable.

    .. versionadded:: 0.9.2
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
        if isinstance(v, type) and v.__name__ == 'param':
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

    If input is a `dict` or `pairs`:

    >>> print build_where({'detail_id': 1, 'age >= ': 20, 'created': date(2013, 4, 16)})
    "created" = '2013-04-16' AND "detail_id" = 1 AND "age" >= 20

    >>> print build_where((('detail_id', 1), ('age >= ', 20), ('created', date(2013, 4, 16))))
    "detail_id" = 1 AND "age" >= 20 AND "created" = '2013-04-16'

    Building prepared where:

    >>> print build_where({'custom_param': param('my_param'), 'auto_param': param, 'using_alias': ___})
    "auto_param" = %(auto_param)s AND "using_alias" = %(using_alias)s AND "custom_param" = %(my_param)s

    It does noting if input is a string:

    >>> print build_where('"detail_id" = 1 AND "age" >= 20 AND "created" = \'2013-04-16\'')
    "detail_id" = 1 AND "age" >= 20 AND "created" = '2013-04-16'

    The default operator will be changed by the value.

    >>> print build_where({'name': None})
    "name" IS NULL

    >>> print build_where({'person_id': ['andy', 'bob']})
    "person_id" IN ('andy', 'bob')

    It is possible to customize your operators:

    >>> print build_where({'email like': '%@gmail.com%'})
    "email" LIKE '%@gmail.com%'

    >>> print build_where({raw('count(person_id) >'): 10})
    count(person_id) > 10

    .. seealso ::
        By default, the operators are limited. Check the :attr:`allowed_operators`
        for more information.
    '''
    return _build_condition(x, identifier, value)

@joiner
def build_set(x):
    r'''A joiner function which builds the set-list of SQL from a `dict` or
    pairs.

    If input is a `dict` or `pairs`:

    >>> print build_set({'a': 1, 'b': True, 'c': date(2013, 4, 16)})
    "a"=1, "c"='2013-04-16', "b"=TRUE

    >>> print build_set((('a', 1), ('b', True), ('c', date(2013, 4, 16))))
    "a"=1, "b"=TRUE, "c"='2013-04-16'

    Building prepared set:

    >>> print build_set({'custom_param': param('myparam'), 'auto_param': param})
    "auto_param"=%(auto_param)s, "custom_param"=%(myparam)s

    It does noting if input is a string:

    >>> print build_set('"a"=1, "b"=TRUE, "c"=\'2013-04-16\'')
    "a"=1, "b"=TRUE, "c"='2013-04-16'
    '''

    ps = _to_pairs(x)

    pieces = []
    for k, v in ps:

        # feature of autoparam
        if isinstance(v, type) and v.__name__ == 'param':
            v = param(k)

        pieces.append('%s=%s' % (identifier(k), value(v)))

    return concat_by_comma(pieces)

@joiner
def build_on(x):
    '''A joiner function which builds the on-list of SQL from a `dict` or pairs.
    The difference from :func:`build_where` is the value here will be treated as
    an identifier.

    >>> print build_on({'person_id': 'friend_id'})
    "person_id" = "friend_id"

    >>> print build_on((('person.person_id', 'detail.person_id'), ))
    "person"."person_id" = "detail"."person_id"

    >>> print build_on({'person.age >': raw(20)})
    "person"."age" > 20
    '''
    return _build_condition(x, identifier, identifier)

# high-level

def or_(conditions):
    '''It concats the conditions by ``OR``.

    .. versionchanged:: 0.7.2
        It helps you to add parens now.

    .. versionadded :: 0.6

    >>> print or_(({'person_id': 'andy'}, {'person_id': 'bob'}))
    ("person_id" = 'andy') OR ("person_id" = 'bob')
    '''

    return concat_by_or(paren(build_where(c)) for c in conditions)

def and_(conditions):
    '''It concats the conditions by ``AND``.

    .. versionadded :: 0.7.3

    >>> print and_(({'person_id': 'andy'}, {'name': 'Andy'}))
    ("person_id" = 'andy') AND ("name" = 'Andy')
    '''

    return concat_by_and(paren(build_where(c)) for c in conditions)

def dot(s, t):
    '''It treats `s` and `t` as identifiers, concats them by ``.``, and then
    makes whole string as :class:`raw`.

    ..versionadded :: 0.9.2
    '''
    return raw('{}.{}'.format(identifier(s), identifier(t)))

def as_(s, t):
    '''It treats `s` and `t` as identifiers, concats them by ``AS``, and then
    makes whole string as :class:`raw`.

    ..versionadded :: 0.9.2
    '''
    return raw('{} AS {}'.format(identifier(s), identifier(t)))

def asc(s):
    '''It treats `s` as an identifier, adds ``ASC`` after `s`, and then makes
    whole string as :class:`raw`.

    ..versionadded :: 0.9.2
    '''
    return raw('{} ASC'.format(identifier(s)))

def desc(s):
    '''It treats `s` as an identifier, adds ``DESC`` after `s`, and then makes
    whole string as :class:`raw`.

    ..versionadded :: 0.9.2
    '''
    return raw('{} DESC'.format(identifier(s)))

def in_operand(x):
    '''It stringifies `x` as an right operand for ``IN``.

    ..versionadded :: 0.9.2
    '''

    if not _is_iterable_not_str(x):
        x = (x, )

    return paren(concat_by_comma(value(x)))

def subq(s):
    '''It adds parens and makes `s` as :class:`raw`.

    ..versionadded :: 0.9.2
    '''
    return raw(paren(s))

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

    The :func:`qualifier` functions:

    .. autosummary ::

        value
        identifier
        paren

    The :func:`joiner` functions:

    .. autosummary ::
        build_where
        build_set
        build_on
        concat_by_comma
        concat_by_and
        concat_by_space
        concat_by_or

    Here is an example of using :class:`Clause`:

    >>> values = Clause('values', (value, concat_by_comma, paren))

    >>> print values.format(('a', 'b', 'c'))
    VALUES ('a', 'b', 'c')

    >>> print values.format((default, 'b', 'c'))
    VALUES (DEFAULT, 'b', 'c')

    >>> print values.format((raw('r'), 'b', 'c'))
    VALUES (r, 'b', 'c')

    .. versionchanged :: 0.9
        Added `no_argument` and made `formatters` has default.

    .. versionchanged :: 0.6
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

    >>> print insert_into_stat.format({
    ...     'insert into': 'person',
    ...     'columns'    : ('person_id', 'name'),
    ...     'values'     : ('daniel', 'Diane Leonard'),
    ... })
    INSERT INTO "person" ("person_id", "name") VALUES ('daniel', 'Diane Leonard')

    .. versionchanged :: 0.6
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
        '''

        if self.preprocessor:
            clause_args = clause_args.copy()
            self.preprocessor(clause_args)

        pieces = []
        for clause in self.clauses:

            # find the arg for this clause
            arg = None
            for possible in clause.possibles:
                if possible in clause_args:
                    arg = clause_args[possible]
                    break

            # if not found and have default, use default
            if arg is None and clause.default:
                arg = clause.default

            # if not found or len(arg) == 0
            if arg:
                pieces.append(clause.format(arg))

        return ' '.join(pieces)

    def __repr__(self):
        return 'Statement(%r)' % self.clauses

def _merge_dicts(default, *updates):
    result = default.copy()
    for update in updates:
        result.update(update)
    return result

class Query(object):
    '''It makes a partial :class:`Statement`.

    :param statement: a statement
    :type statement: :class:`Statement`
    :param positional_keys: the positional arguments accepted by :meth:`stringify`.
    :type positional_keys: sequence
    :param clause_args: the arguments of the clauses you want to predefine
    :type clause_args: dict

    .. versionadded :: 0.6
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
        '''It is same as the :meth:`format`, but it let you use keyword
        arguments.

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
        return 'Query({}, ** {})'.format(', '.join(
            '{}=None'.format(k)
            for k in self.positional_keys
        ), ', '.join(
            '{}=None'.format(clause.prefix.lower().replace(' ', '_'))
            for clause in self.statement.clauses
        ))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
