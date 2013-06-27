#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains the basic SQL builders.

.. versionchanged:: 0.1.6
    It is rewritten and totally different from old version.

It is designed for standard SQL and tested in PostgreSQL. If your database uses
non-standard SQL, you may need to customize and override the following
functions.

.. autosummary ::
    escape
    format_param
    stringify_bool
    delimit_identifier
    escape_identifier

.. note::
    Here is a patch for MySQL --- :mod:`mosql.mysql`.

If you need you own SQL statements, the following classes may help you.

.. autosummary ::
    Clause
    Statement
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
    'Clause', 'Statement',
]

from functools import wraps
from datetime import datetime, date, time

def escape(s):
    '''The function which escapes the value.

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

def format_param(s=''):
    '''The function which format the parameter of prepared statement.

    By default, it formats the parameter in `pyformat
    <http://www.python.org/dev/peps/pep-0249/#paramstyle>`_.

    >>> format_param('name')
    '%(name)s'

    >>> format_param()
    '%s'
    '''
    return '%%(%s)s' % s if s else '%s'

def stringify_bool(b):
    '''The function which stringifies the bool.

    By default, it returns ``'TRUE'`` if `b` is true, otherwise it returns
    ``'FALSE'``.
    '''
    return 'TRUE' if b else 'FALSE'

def delimit_identifier(s):
    '''The function which delimits the identifier.

    By default, it conforms the standard to encloses the identifier, `s`, by "
    (double quote).

    .. note ::
        It is disableable. Set it ``None`` to disable the feature of delimiting
        identifiers. But you have responsibility to ensure the security if you
        disable it.
    '''
    return '"%s"' % s

def escape_identifier(s):
    '''The function which escapes the identifier.

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

class raw(str):
    '''This is a subclass of built-in `str` type. The qualifier function do
    noting when the input is an instance of this class

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
    ''':func:`value` builds this type as a parameter for the prepared statement

    >>> value(param(''))
    '%s'
    >>> value(param('name'))
    '%(name)s'

    This is just a subclass of built-in `str` type.
    '''

    def __repr__(self):
        return 'param(%s)' % self

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

_type_value_map = {
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
    '''It is a qualifier function for values.

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
        handler =  _type_value_map.get(type(x))
        if handler:
            return handler(x)
        else:
            for t in _type_value_map:
                if isinstance(x, t):
                    return _type_value_map[t](x)
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
    '''It is a qualifier function for identifiers.

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
    '''It is a qualifier function which encloses the input with () (paren).'''
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

@joiner
def build_where(x):
    '''It is a joiner function which builds the where list of SQL from a `dict`
    or `pairs`.

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
        v = value(v)
        if _is_iterable_not_str(v):
            v = paren(concat_by_comma(v))

        # qualify the k
        k = identifier(k)

        if op:
            pieces.append('%s %s %s' % (k, op, v))
        else:
            pieces.append('%s %s' % (k, v))

    return concat_by_and(pieces)

@joiner
def build_set(x):
    '''It is a joiner function which builds the set list of SQL from a `dict` or
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
    '''It is a joiner function which builds the simple (the operator is always
    =) on list of SQL from a `dict` or pairs.

    >>> print build_on({'person.person_id': 'detail.person_id'})
    "person"."person_id" = "detail"."person_id"

    >>> print build_on((('person.person_id', 'detail.person_id'), ))
    "person"."person_id" = "detail"."person_id"
    '''

    ps = _to_pairs(x)

    pieces = []
    for k, v in ps:
        pieces.append('%s = %s' % (identifier(k), identifier(v)))

    return concat_by_and(pieces)

# NOTE: To keep simple, the below classes shouldn't rely on the above functions

class Clause(object):
    '''It represents a clause of SQL.

    :param prefix: the lead word(s) of this clause
    :type prefix: str

    :param formatters: the qualifier or joiner functions
    :type formatters: iterable

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
            arg = clause_args.get(clause.prefix.lower())
            # NOTE: for backward compatibility
            #if arg is not None:
            if arg:
                pieces.append(clause.format(arg))
        return ' '.join(pieces)

    def __repr__(self):
        return 'Statement(%s)' % self.clauses

if __name__ == '__main__':
    import doctest
    doctest.testmod()
