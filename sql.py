#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains some useful funtions to build SQL with common Python's data type.'''

# The default styles of ``dumps``
paramstyle = 'pyformat'
boolstyle  = 'uppercase'

# A hyper None, because None represents null in SQL.
Empty = ___ = type('Empty', (object,), {
    '__nonzero__': lambda self: False,
    '__repr__'   : lambda self: '___',
})()

def splitop(s):
    op = None
    space_pos = s.rfind(' ')
    if space_pos != -1:
        s, op = s[:space_pos], s[space_pos+1:]
    return s, op

from datetime import date, time, datetime

def dumps(x, **format):
    '''Dump any object ``x`` into SQL's representation.

    Return a string.

    The basic types:

    >>> print dumps(None)
    null

    >>> print dumps(True), dumps(False)
    TRUE FALSE

    >>> print dumps(True, boolstyle='bit'), dumps(False, boolstyle='bit')
    1 0

    The ``boolstyle`` can be `uppercase` or `bit`.

    >>> print dumps(123)
    123

    >>> print dumps(123, val=True)
    123

    >>> print dumps('var')
    var

    >>> print dumps('val', val=True)
    'val'

    The sequences:

    >>> print dumps(('a', 'b', 'c'))
    a, b, c

    >>> print dumps(('a', 'b', 'c'), parens=True)
    (a, b, c)

    >>> print dumps(('a', 'b', 'c'), val=True)
    'a', 'b', 'c'

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True)
    ('a', 'b', 'c')

    Actually, you can use any non-mapping iterable to build the above strings.

    The mappings:

    >>> print dumps({'a': 1, 'b': 'str'}, val=True)
    a = 1, b = 'str'

    >>> print dumps({'a >=': 1, 'b': ('x', 'y')}, val=True, parens=True, condition=True)
    b IN ('x', 'y') AND a >= 1

    The prepared statements with formating parameter, ``param``:

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True, param=True)
    (%(a)s, %(b)s, %(c)s)

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True, param=True, paramstyle='qmark')
    (?, ?, ?)

    The ``paramstyle`` can be `pyformat`, `qmark`, `named` or `format`. The `numberic` isn't supported yet.

    >>> print dumps({'a >=': 'a', 'b': 'b'}, val=True, param=True, condition=True)
    b = %(b)s AND a >= %(a)s

    The prepared statement with Empty object, ``___`` (triple-underscore).

    >>> print dumps({'a >=': 1, 'b': ___ }, val=True, condition=True)
    b = %(b)s AND a >= 1

    >>> print dumps({'a >=': ___ , 'b': ___ }, val=True, condition=True)
    b = %(b)s AND a >= %(a)s

    >>> print dumps((___, 'b', 'c'), val=True, parens=True, paramkeys=('x', 'y', 'z'))
    (%(x)s, 'b', 'c')
    '''

    global paramstyle, boolstyle

    if isinstance(x, unicode):
        x = x.encode(format.get('encoding', 'UTF-8'))

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
            return "'%s'" % x.replace("'", "''")
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

    Here is an example of SQL's `select ...` statement:

    >>> sql = SQL(
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

    If you want to know what fields it have, the attribute, ``field_names``, could help you.

    >>> sql.field_names == set(
    ...     ['select', 'table', 'where', 'group_by', 'having', 'order_by', 'limit', 'offset']
    ... )
    True
    '''

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
        '''It supports using attribute to update field.

        >>> sql = SQL(('key', '<value>'))
        >>> sql.value = 'data'
        >>> print sql
        KEY data;
        '''

        field_names = getattr(self, 'field_names', None)
        if field_names and key in field_names:
            self.filled[key] = value
            self.cached = None
        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        '''It supports using attribute to get value of field.

        >>> sql = SQL(('key', '<value>'))
        >>> sql.value = 'data'

        >>> print sql.value
        data

        >>> print sql.x
        Traceback (most recent call last):
            ...
        KeyError: 'x'
        '''

        field_names = object.__getattribute__(self, 'field_names')
        return self.filled[key]

    def __str__(self):
        '''Render given SQL template by filled field.'''

        if self.cached: return self.cached

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
                            rendered = dumps(value, val=True, parens=True, condition=True, **self.format)
                        elif key == 'set':
                            rendered = dumps(value, val=True, parens=True, **self.format)
                        elif key == 'pairs':
                                self.filled['columns'], self.filled['values'] = zip(*value.items())
                        elif key == 'values':
                            rendered = dumps(value, val=True, parens=True, paramkeys=self.filled.get('columns'), **self.format)
                        elif key == 'columns':
                            rendered = dumps(value, parens=True, **self.format)
                        else:
                            rendered = dumps(value, **self.format)

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

def insert(table, **fields):
    '''It is a shortcut for the SQL statement, ``insert into ...``.

    Return: a ``SQL`` instance

    Examples:

    >>> print insert('users', pairs={'id': 'mosky'})
    INSERT INTO users (id) VALUES ('mosky');

    >>> print insert('users', pairs={'id': ___ })
    INSERT INTO users (id) VALUES (%(id)s);

    >>> print insert('users', values=('mosky', 'Mosky Liu', 'mosky.tw@gmail.com'))
    INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky.tw@gmail.com');

    >>> print insert('users', columns=('email', 'id', 'name'), values=('mosky.tw@gmail.com', 'mosky', 'Mosky Liu'))
    INSERT INTO users (email, id, name) VALUES ('mosky.tw@gmail.com', 'mosky', 'Mosky Liu');

    >>> insert('users').field_names == set(
    ...     ['table', 'pairs', 'values', 'columns', 'returning']
    ... )
    True
    '''

    sql = SQL(
        # The <pairs> could be a dict or iterable (prepared statement),
        # It will be disassembled into <columns> and <values>.
        ('<pairs>', ),
        # It is a template group, and
        # it only be rendered if every <field> is be filled.
        ('insert into', '<table>'),
        # It is another template group.
        ('<columns>', ),
        ('values', '<values>'),
        ('returning', '<returning>'),
    )
    fields['table'] = table
    sql.update(fields)
    return sql

def select(table, **fields):
    '''It is a shortcut for the SQL statement, ``select ...``.

    Return: a ``SQL`` instance

    Examples:

    >>> print select('users')
    SELECT * FROM users;

    >>> print select('users', order_by='id')
    SELECT * FROM users ORDER BY id;

    >>> print select('users', select='id', order_by=('id DESC', 'email'))
    SELECT id FROM users ORDER BY id DESC, email;

    >>> print select('users', limit=1, where={'id': 'mosky'})
    SELECT * FROM users WHERE id = 'mosky' LIMIT 1;

    >>> print select('users', where={'id': ('mosky', 'moskytw')})
    SELECT * FROM users WHERE id IN ('mosky', 'moskytw');

    >>> print select('users', where={'email like': '%@gmail.com'})
    SELECT * FROM users WHERE email LIKE '%@gmail.com';

    >>> print select('users', where={'name': ___, 'email': ___ })
    SELECT * FROM users WHERE name = %(name)s AND email = %(email)s;

    >>> sql = select('users', where={'name': ___, 'email': ___ })
    >>> sql.format['paramstyle'] = 'qmark'
    >>> print sql
    SELECT * FROM users WHERE name = ? AND email = ?;

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
    sql.update(fields)
    return sql

def update(table, **fields):
    '''It is a shortcut for the SQL statement, ``update ...``.

    Return: a ``SQL`` instance

    Examples:

    >>> print update('users', set={'email': 'mosky.tw@gmail.com'}, where={'id': 'mosky'})
    UPDATE users SET email = 'mosky.tw@gmail.com' WHERE id = 'mosky';

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
    sql.update(fields)
    return sql

def delete(table, **fields):
    '''It is a shortcut for the SQL statement, ``delete from ...``.

    Return: a ``SQL`` instance

    Examples:

    >>> print delete('users', where={'id': 'mosky'})
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
    sql.update(fields)
    return sql

if __name__ == '__main__':
    import doctest
    doctest.testmod()
