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
    'OptionError', 'allowed_options', 'identifier',
    'joiner',
    'concat_by_comma', 'concat_by_and', 'concat_by_space', 'concat_by_or',
    'OperatorError', 'allowed_operators',
    'build_where', 'build_set', 'build_on',
    'or_',
    'Clause', 'Statement', 'Query',
]

from functools import wraps
from datetime import datetime, date, time

import sys
if sys.version_info[0] == 3:
    str = str
    unicode = str
    basestring = (str, bytes)

def escape(s):
    '''It escapes the value.

    By default, it just replaces ' (single-quote) with '' (two single-quotes).

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
    '''
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

    By default, it conforms the standard to encloses the identifier, `s`, by "
    (double quote).

    .. note ::
        It is disableable. Set it ``None`` to disable the feature of delimiting
        identifiers. But you have responsibility to ensure the security if you
        disable it.
    '''
    return '"%s"' % s

std_delimit_identifier = delimit_identifier

def escape_identifier(s):
    '''It escapes the identifier.

    By default, it just replaces " (double-quote) with "" (two double-quotes).

    It also aims at avoid SQL injection. Here are some examples:

    >>> tmpl = 'select * from person where "%s" = \\'mosky\\';'
    >>> evil_value = 'person_id" = \\'\\' or true; -- '

    >>> print tmpl % evil_value
    select * from person where "person_id" = '' or true; -- " = 'mosky';

    >>> print tmpl % escape_identifier(evil_value)
    select * from person where "person_id"" = '' or true; -- " = 'mosky';
    '''
    return s.replace('"', '""')

std_escape_identifier = escape_identifier

class raw(str):
    '''The qualifier function do noting when the input is an instance of this
    class. This is a subclass of built-in `str` type.

    .. warning ::
        You have responsibility to ensure the security if you use this class.
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

def _quote_str(x):
    return "'%s'" % escape(x)

def _quote_datetime(x):
    return "'%s'" % x

_type_handler_map = {
    str     : _quote_str,
    unicode : _quote_str,
    bool    : stringify_bool,
    datetime: _quote_datetime,
    date    : _quote_datetime,
    time    : _quote_datetime,
    raw     : lambda x: x,
    # it should be a lazy evaluation to be patchable
    param   : lambda x: format_param(x),
}

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

    if x is None:
        return 'NULL'
    else:
        handler =  _type_handler_map.get(type(x))
        if handler:
            return handler(x)
        else:
            for t in _type_handler_map:
                if isinstance(x, t):
                    return _type_handler_map[t](x)
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

.. note ::
    It is disableable. Set it ``None`` to disable the feature of checking the
    option. But you have responsibility to ensure the security if you disable
    it.
'''

@qualifier
def identifier(s):
    '''A qualifier function for identifiers.

    It uses the :func:`delimit_identifier` and :func:`escape_identifier` to
    qualifiy the input.

    It returns the input with no changes if :func:`delimit_identifier` is
    ``None``.

    >>> print identifier('column_name')
    "column_name"

    >>> print identifier('column_name desc')
    "column_name" DESC

    >>> print identifier('table_name.column_name')
    "table_name"."column_name"

    >>> print identifier('table_name.column_name DESC')
    "table_name"."column_name" DESC
    '''

    if delimit_identifier is None:
        return s
    elif s.find('.') == -1 and s.find(' ') == -1:
        return delimit_identifier(escape_identifier(s))
    else:

        t, _, c = s.rpartition('.')
        c, _, op = c.partition(' ')

        r = ''

        if t:
            t = delimit_identifier(escape_identifier(t))
            r += t+'.'

        if c:
            c = delimit_identifier(escape_identifier(c))
            r += c

        if op:
            op = op.upper()
            if allowed_options is not None and op not in allowed_options:
                raise OptionError(op)
            r += ' '+op

        return r

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
    '''A joiner function which concats the iterable by , (comma).'''
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

.. note ::
    It is disableable. Set it ``None`` to disable the feature of checking the
    operator. But you have responsibility to ensure the security if you disable
    it.
'''

def _to_pairs(x):

    if hasattr(x, 'iteritems'):
        x = x.iteritems()
    elif hasattr(x, 'items'):
        x = x.items()

    return x

def _build_condition(x, key_qualify=identifier, value_qualifier=value):

    ps = _to_pairs(x)

    pieces = []

    for k, v in ps:

        # find the op

        op = ''

        if not isinstance(k, raw):

            # split the op out
            space_pos = k.find(' ')
            if space_pos != -1:
                k, op = k[:space_pos], k[space_pos+1:].strip()

            if not op:
                if _is_iterable_not_str(v):
                    op = 'IN'
                elif v is None:
                    op = 'IS'
                else:
                    op = '='
            else:
                op = op.upper()
                if allowed_operators is not None and op not in allowed_operators:
                    raise OperatorError(op)

        # feature of autoparam
        if isinstance(v, type) and v.__name__ == 'param':
            v = param(k)

        # qualify the v
        v = value_qualifier(v)
        if _is_iterable_not_str(v):
            v = paren(concat_by_comma(v))

        # qualify the k
        k = key_qualify(k)

        if op:
            pieces.append('%s %s %s' % (k, op, v))
        else:
            pieces.append('%s %s' % (k, v))

    return concat_by_and(pieces)

@joiner
def build_where(x):
    '''A joiner function which builds the where-list of SQL from a `dict` or
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

    >>> print build_where('"detail_id" = 1 AND "age" >= 20 AND "created" = \\'2013-04-16\\'')
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
    '''A joiner function which builds the set-list of SQL from a `dict` or
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

    >>> print build_set('"a"=1, "b"=TRUE, "c"=\\'2013-04-16\\'')
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

def or_(conditions):
    '''It concats the conditions by ``OR``.

    .. versionadded :: 0.6

    >>> print or_(({'person_id': 'andy'}, {'person_id': 'bob'}))
    "person_id" = 'andy' OR "person_id" = 'bob'
    '''

    return concat_by_or(build_where(c) for c in conditions)

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

    .. versionchanged :: 0.6
        Added two arguments, `alias` and `default`.
    '''

    def __init__(self, name, formatters, hidden=False, alias=None, default=None):

        self.prefix = name.upper()
        self.formatters = formatters
        self.hidden = hidden

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

        for formatter in self.formatters:
            x = formatter(x)

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

            arg = None
            for possible in clause.possibles:
                try:
                    arg = clause_args[possible]
                except KeyError:
                    continue
                else:
                    break

            if arg is None and clause.default:
                arg = clause.default

            if arg is not None:
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
        '''It is same as the :meth:`stringify`. It is for backward-compatibility, and not encourage to use.'''
        return self.stringify(*positional_values, **clause_args)

    def __repr__(self):
        return 'Query(%r, %r, %r)' % (self.statement, self.positional_keys, self.clause_args)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
