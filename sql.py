#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains some useful funtions to build SQL with common Python's data type.'''

# The default styles of ``dumps``
encoding   = 'UTF-8'
paramstyle = 'pyformat'
boolstyle  = 'uppercase'

# A hyper None, because None represents null in SQL.
Empty = ___ = type('Empty', (object,), {
    '__nonzero__': lambda self: False,
    '__repr__'   : lambda self: '___',
})()

def escape(s):
    '''Replace the ``'`` (single quote) by ``''`` (two single quote).

    :param s: a string which you want to escape.
    :type s: str
    :rtype: str

    >>> print dumps("'DROP TABLE users; --", val=True)
    '\''DROP TABLE users; --'

    .. warning::
        In MySQL, it only ensures the security in ANSI mode by default.

    .. seealso::
        How :py:mod:`~sql` dumps the Python's object to SQL -- :py:func:`~sql.dumps`.
    '''
    return s.replace("'", "''")

def splitop(s):
    '''Split `s` by rightmost space into the right string and a string operator in a 2-tuple.

    :param s: a string which you want to split.
    :type s: str
    :rtype: 2-tuple

    >>> print splitop('withoutop')
    ('withoutop', None)

    >>> print splitop('with op')
    ('with', 'op')
    '''
    op = None
    space_pos = s.rfind(' ')
    if space_pos != -1:
        s, op = s[:space_pos], s[space_pos+1:]
    return s, op

from datetime import date, time, datetime

def dumps(x, **format):
    '''Dump any object `x` into SQL's representation.

    :param x: any object.
    :param format: the formating parameters.
    :type format: dict

    The examples of basic types:

    >>> print dumps(None)
    null

    >>> print dumps(True), dumps(False)
    TRUE FALSE

    >>> print dumps(True, boolstyle='bit'), dumps(False, boolstyle='bit')
    1 0

    The `boolstyle` can be `uppercase` or `bit`.

    >>> print dumps(123)
    123

    >>> print dumps(123, val=True)
    123

    >>> print dumps('var')
    var

    >>> print dumps('val', val=True)
    'val'

    The examples of `sequences`:

    >>> print dumps(('a', 'b', 'c'))
    a, b, c

    >>> print dumps(('a', 'b', 'c'), parens=True)
    (a, b, c)

    >>> print dumps(('a', 'b', 'c'), val=True)
    'a', 'b', 'c'

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True)
    ('a', 'b', 'c')

    Actually, you can use any `iterable` to build the above strings, except `mapping`.

    The examples of `mapping`:

    >>> print dumps({'a': 1, 'b': 'str'}, val=True)
    a = 1, b = 'str'

    >>> print dumps({'a >=': 1, 'b': ('x', 'y')}, val=True, parens=True, condition=True)
    b IN ('x', 'y') AND a >= 1

    The prepared statements made with formating parameter, ``param``:

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True, param=True)
    (%(a)s, %(b)s, %(c)s)

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True, param=True, paramstyle='qmark')
    (?, ?, ?)

    The `paramstyle` can be `pyformat`, `qmark`, `named` or `format`. The `numberic` isn't supported yet.

    >>> print dumps({'a >=': 'a', 'b': 'b'}, val=True, param=True, condition=True)
    b = %(b)s AND a >= %(a)s

    The prepared statement made with :py:class:`Empty` object, ``___`` (triple-underscore).

    >>> print dumps({'a >=': 1, 'b': ___ }, val=True, condition=True)
    b = %(b)s AND a >= 1

    >>> print dumps({'a >=': ___ , 'b': ___ }, val=True, condition=True)
    b = %(b)s AND a >= %(a)s

    >>> print dumps((___, 'b', 'c'), val=True, parens=True, paramkeys=('x', 'y', 'z'))
    (%(x)s, 'b', 'c')
    '''

    global paramstyle, boolstyle

    if isinstance(x, unicode):
        x = x.encode(format.get('encoding', encoding))

    param = format.get('param')
    paramkey = format.get('paramkey')
    if (
        (param and isinstance(x, (str, int))) or
        (x is Empty and paramkey)
    ):
        if x is Empty:
            x = paramkey

        _paramstyle = format.get('paramstyle', paramstyle)
        if _paramstyle == 'pyformat':
            return '%%(%s)s' % x
        elif _paramstyle == 'qmark':
            return '?'
        elif _paramstyle == 'named':
            return ':%s' % x
        elif _paramstyle == 'format':
            return '%s'
        elif _paramstyle == 'numberic':
            return ':%d' % x

    if isinstance(x, str):
        if format.get('val'):
            return "'%s'" % format.get('escape', escape)(x)
        else:
            return x

    if isinstance(x, bool):
        _boolstyle = format.get('boolstyle', boolstyle)
        if _boolstyle == 'uppercase':
            return 'TRUE' if x else 'FALSE'
        elif _boolstyle == 'bit':
            return 1 if x else 0

    if isinstance(x, (int, float, long, datetime, date, time)):
        return str(x)

    if hasattr(x, 'items'):

        operations = []
        format = format.copy()
        for k, v in x.items():

            # find the operator in key
            k, op = splitop(k)
            if op is None:
                if not isinstance(v, basestring) and hasattr(v, '__iter__'):
                    op = 'in'
                else:
                    op = '='

            # let value replace by the param if value is ``___``
            format['paramkey'] = k

            operations.append('%s %s %s' % (
                dumps(k),
                op.upper(),
                dumps(v, **format),
            ))

        if format.get('condition'):
            return ' AND '.join(operations)
        else:
            return ', '.join(operations)

    if hasattr(x, '__iter__'):

        paramkeys = format.get('paramkeys')
        if paramkeys:
            s = ', '.join(dumps(v, paramkey=k, **format) for v, k in zip(x, paramkeys))
        else:
            s = ', '.join(dumps(v, **format) for v in x)

        if format.get('parens'):
            s = '(%s)' % s
        return s

    if x is None:
        return 'null'

    return str(x)

class SQL(object):
    '''It builds a SQL statement by given template.

    :param template_groups: the template groups.
    :type template_groups: two-level nest tuple

    Here is an example of SQL's `select ...` statement:

    >>> sql_select = SQL(
    ...     # It is a template group, and
    ...     # it only be rendered if every <field> is be filled.
    ...     ('select', '<select>'),
    ...     # It is another template group.
    ...     ('from', '<table>'),
    ...     ('where', '<where>'),
    ...     ('group by', '<group_by>'),
    ...     ('having', '<having>'),
    ...     ('order by', '<order_by>'),
    ...     ('limit', '<limit>'),
    ...     ('offset', '<offset>'),
    ... )

    It supports using attributes to access fields.

    >>> sql = SQL(('key', '<value>'))
    >>> sql.value = 'data'
    >>> print sql
    KEY data;
    >>> print sql.value
    data
    >>> print sql.x
    Traceback (most recent call last):
        ...
    KeyError: 'x'

    If you want to know what fields it has, the attribute, ``field_names``, could help you.

    >>> sql_select.field_names == set(
    ...     ['select', 'table', 'where', 'group_by', 'having', 'order_by', 'limit', 'offset']
    ... )
    True
    '''

    format = {}

    def __init__(self, *template_groups):
        self.template_groups = template_groups
        self.field_names = set()
        for template_group in template_groups:
            for template in template_group:
                if template.startswith('<'):
                    self.field_names.add(template[1:-1])
        self.filled = {}
        self.cached = None
        self.format = {}

    def update(self, dict):
        '''Use a dict to update the fields' values.'''
        self.filled.update(dict)

    def __setattr__(self, key, value):
        field_names = getattr(self, 'field_names', None)
        if field_names and key in field_names:
            self.filled[key] = value
            self.cached = None
        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        field_names = object.__getattribute__(self, 'field_names')
        return self.filled[key]

    def __str__(self):

        if self.cached: return self.cached

        format = self.format.copy()
        format.update(self.__class__.format)
        sql_components = []

        for template_group in self.template_groups:

            # starts to render a template group
            rendered_templates = []
            for template in template_group:

                # if it need to be substitute
                if template.startswith('<'):

                    key = template[1:-1]
                    value = self.filled.get(key, Empty)
                    rendered = None

                    # handles special cases
                    # TODO: it could be abstracted as a parameter of initialization
                    if value is Empty:
                        if key == 'select':
                            rendered = '*'
                    else:
                        if key in ('where', 'having'):
                            rendered = dumps(value, val=True, parens=True, condition=True, **format)
                        elif key == 'set':
                            rendered = dumps(value, val=True, parens=True, **format)
                        elif key == 'mapping':
                                self.filled['columns'], self.filled['values'] = zip(*value.items())
                        elif key == 'values':
                            rendered = dumps(value, val=True, parens=True, paramkeys=self.filled.get('columns'), **format)
                        elif key == 'multi_values':
                            rendered = dumps((dumps(i, val=True, parens=True, **format) for i in value))
                        elif key == 'columns':
                            rendered = dumps(value, parens=True, **format)
                        else:
                            rendered = dumps(value, **format)

                    rendered_templates.append(rendered)
                else:
                    rendered_templates.append(template.upper())

            # all of the templates in a group must be rendered
            if all(rendered_templates):
                sql_components.append(' '.join(rendered_templates))

        self.cached = ' '.join(sql_components)+';'
        return self.cached

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(repr(t) for t in self.template_groups)
        )

def insert(table, mapping=None, **fields):
    '''It is a shortcut for the SQL statement, ``insert into ...`` .

    :param table: the name of database's table
    :type table: str
    :param mapping: the data prepared to insert into database
    :type mapping: mapping
    :param fields: the other fileds
    :type fields: dict
    :rtype: :py:class:`~sql.SQL`

    The examples:

    >>> print insert('users', {'id': 'mosky'})
    INSERT INTO users (id) VALUES ('mosky');

    >>> print insert('users', {'id': ___ })
    INSERT INTO users (id) VALUES (%(id)s);

    The ``mapping`` is added by this libaray. It is for convenience and not a part of SQL.

    >>> print insert('users', values=('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'))
    INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com');

    >>> print insert('users', columns=('email', 'id', 'name'), values=('mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu'))
    INSERT INTO users (email, id, name) VALUES ('mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu');

    >>> print insert('users', multi_values=(('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'), ('moskytw', 'Mosky Liu', 'mosky DOT liu AT pinkoi.com')))
    INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'), ('moskytw', 'Mosky Liu', 'mosky DOT liu AT pinkoi.com');

    >>> insert('users').field_names == set(
    ...     ['table', 'mapping', 'values', 'multi_values', 'columns', 'returning']
    ... )
    True
    '''

    sql = SQL(
        # The <mapping> could be a dict or iterable (prepared statement),
        # It will be disassembled into <columns> and <values>.
        ('<mapping>', ),
        # It is a template group, and
        # it only be rendered if every <field> is be filled.
        ('insert into', '<table>'),
        # It is another template group.
        ('<columns>', ),
        ('values', '<values>'),
        ('values', '<multi_values>'),
        ('returning', '<returning>'),
    )
    fields['table'] = table
    if mapping:
        fields['mapping'] = mapping
    sql.update(fields)
    return sql

def select(table, where=None, **fields):
    '''It is a shortcut for the SQL statement, ``select ...`` .

    :param table: the name of database's table
    :type table: str
    :param where: the conditions represented in a mapping
    :type where: mapping
    :param fields: the other fileds
    :type fields: dict
    :rtype: :py:class:`~sql.SQL`

    The examples:

    >>> print select('users', {'id': 'mosky'})
    SELECT * FROM users WHERE id = 'mosky';

    >>> print select('users')
    SELECT * FROM users;

    >>> print select('users', order_by='id')
    SELECT * FROM users ORDER BY id;

    >>> print select('users', select='email', order_by=('email DESC', 'id'))
    SELECT email FROM users ORDER BY email DESC, id;

    >>> print select('users', where={'id': ('mosky', 'moskytw')})
    SELECT * FROM users WHERE id IN ('mosky', 'moskytw');

    >>> print select('users', where={'email like': '%@gmail.com'})
    SELECT * FROM users WHERE email LIKE '%@gmail.com';

    >>> print select('users', where={'name': ___, 'email': 'mosky DOT tw AT gmail.com' })
    SELECT * FROM users WHERE name = %(name)s AND email = 'mosky DOT tw AT gmail.com';

    The ``format`` parameter on class's level:

    >>> SQL.format['paramstyle'] = 'qmark'
    >>> print select('users', where={'name': ___, 'email': 'mosky DOT tw AT gmail.com' })
    SELECT * FROM users WHERE name = ? AND email = 'mosky DOT tw AT gmail.com';
    >>> SQL.format.clear()

    The ``format`` parameter on instance's level:

    >>> sql = select('users', where={'name': ___, 'email': 'mosky DOT tw AT gmail.com' })
    >>> sql.format['paramstyle'] = 'qmark'
    >>> print sql
    SELECT * FROM users WHERE name = ? AND email = 'mosky DOT tw AT gmail.com';

    >>> select('users').field_names == set(
    ...     ['select', 'table', 'where', 'group_by', 'having', 'order_by', 'limit', 'offset']
    ... )
    True
    '''

    sql = SQL(
        ('select', '<select>'),
        ('from', '<table>'),
        ('where', '<where>'),
        ('group by', '<group_by>'),
        ('having', '<having>'),
        ('order by', '<order_by>'),
        ('limit', '<limit>'),
        ('offset', '<offset>'),
    )
    fields['table'] = table
    if where:
        fields['where'] = where
    sql.update(fields)
    return sql

def update(table, where=None, set=None, **fields):
    '''It is a shortcut for the SQL statement, ``update ...`` .

    :param table: the name of database's table
    :type table: str
    :param where: the conditions represented in a mapping
    :type where: mapping
    :param set: the part you want to update
    :type set: mapping
    :param fields: the other fileds
    :type fields: dict
    :rtype: :py:class:`~sql.SQL`

    The examples:

    >>> print update('users', {'id': 'mosky'}, {'email': 'mosky DOT tw AT gmail.com'})
    UPDATE users SET email = 'mosky DOT tw AT gmail.com' WHERE id = 'mosky';

    >>> update('users').field_names == set(
    ...     ['table', 'set', 'where', 'returning']
    ... )
    True
    '''

    sql = SQL(
        ('update', '<table>'),
        ('set', '<set>'),
        ('where', '<where>'),
        ('returning', '<returning>'),
    )
    fields['table'] = table
    if where:
        fields['where'] = where
    if set:
        fields['set'] = set
    sql.update(fields)
    return sql

def delete(table, where=None, **fields):
    '''It is a shortcut for the SQL statement, ``delete from ...`` .

    :param table: the name of database's table
    :type table: str
    :param where: the conditions represented in a mapping
    :type where: mapping
    :param fields: the other fileds
    :type fields: dict
    :rtype: :py:class:`~sql.SQL`

    The examples:

    >>> print delete('users', {'id': 'mosky'})
    DELETE FROM users WHERE id = 'mosky';

    >>> delete('users').field_names == set(
    ...     ['table', 'where', 'returning']
    ... )
    True
    '''

    sql = SQL(
        ('delete from', '<table>'),
        ('where', '<where>'),
        ('returning', '<returning>'),
    )
    fields['table'] = table
    if where:
        fields['where'] = where
    sql.update(fields)
    return sql

if __name__ == '__main__':
    import doctest
    doctest.testmod()
