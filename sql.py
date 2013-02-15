#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains useful functions to build SQL with common Python's data types.'''

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
    '''Replace the ``'`` (single quote) by ``''`` (two single quotes).

    :param s: a string which you want to escape
    :type s: str
    :rtype: str

    >>> print dumps("'DROP TABLE users; --", val=True)
    '\''DROP TABLE users; --'

    .. warning::
        In MySQL, it only ensures the security in ANSI mode by default.

    .. note::
        When using :py:class:`~sql.SQLTemplate`, you can replace this function by assigning a function to the formating specification, ``escape``.
    '''
    return s.replace("'", "''")

def splitop(s):
    '''Split `s` by rightmost space into the left string and a string operator in a 2-tuple.

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

def dumps(x, **format_spec):
    '''Dump any object `x` into SQL's representation.

    :param x: any object
    :param format_spec: the formating specification
    :type format_spec: mapping

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

    Actually, you can use any `iterable` to build the above strings, except mapping.

    The examples of `mapping`:

    >>> print dumps({'a': 1, 'b': 'str'})
    a = 1, b = 'str'

    >>> print dumps({'a >=': 1, 'b': ('x', 'y')}, condition=True)
    b IN ('x', 'y') AND a >= 1

    The example of using ``param`` to build `prepared statement`:

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True, param=True)
    (%(a)s, %(b)s, %(c)s)

    >>> print dumps(('a', 'b', 'c'), val=True, parens=True, param=True, paramstyle='qmark')
    (?, ?, ?)

    The `paramstyle` can be `pyformat`, `qmark`, `named` or `format_spec`. The `numberic` isn't supported yet.

    >>> print dumps({'a >=': 'a', 'b': 'b'}, param=True, condition=True)
    b = %(b)s AND a >= %(a)s

    The example of using :py:class:`Empty` object, ``___`` (triple-underscore) to build `prepared statement`.

    >>> print dumps({'a >=': 1, 'b': ___ }, condition=True)
    b = %(b)s AND a >= 1

    >>> print dumps({'a >=': ___ , 'b': ___ }, condition=True)
    b = %(b)s AND a >= %(a)s

    >>> print dumps((___, 'b', 'c'), val=True, parens=True, paramkeys=('x', 'y', 'z'))
    (%(x)s, 'b', 'c')
    '''

    global paramstyle, boolstyle

    if isinstance(x, unicode):
        x = x.encode(format_spec.get('encoding', encoding))

    param = format_spec.get('param')
    paramkey = format_spec.get('paramkey')
    if (
        (param and isinstance(x, (str, int))) or
        (x is Empty and paramkey)
    ):
        if x is Empty:
            x = paramkey

        _paramstyle = format_spec.get('paramstyle', paramstyle)
        if _paramstyle == 'pyformat':
            return '%%(%s)s' % x
        elif _paramstyle == 'qmark':
            return '?'
        elif _paramstyle == 'named':
            return ':%s' % x
        elif _paramstyle == 'format_spec':
            return '%s'
        elif _paramstyle == 'numberic':
            return ':%d' % x

    if isinstance(x, str):
        if format_spec.get('val'):
            return "'%s'" % format_spec.get('escape', escape)(x)
        else:
            return x

    if isinstance(x, bool):
        _boolstyle = format_spec.get('boolstyle', boolstyle)
        if _boolstyle == 'uppercase':
            return 'TRUE' if x else 'FALSE'
        elif _boolstyle == 'bit':
            return 1 if x else 0

    if isinstance(x, (int, float, long, datetime, date, time)):
        return str(x)

    if hasattr(x, 'items'):

        operations = []
        format_spec = format_spec.copy()
        for k, v in x.items():

            # find the operator in key
            k, op = splitop(k)
            if op is None:
                if not isinstance(v, basestring) and hasattr(v, '__iter__'):
                    op = 'in'
                else:
                    op = '='

            # let value replace by the param if value is ``___``
            format_spec['paramkey'] = k

            # set val and parens for value
            value_format_spec = format_spec.copy()
            value_format_spec['val'] = True
            value_format_spec['parens'] = True

            operations.append('%s %s %s' % (
                dumps(k),
                op.upper(),
                dumps(v, **value_format_spec),
            ))

        if format_spec.get('condition'):
            return ' AND '.join(operations)
        else:
            return ', '.join(operations)

    if hasattr(x, '__iter__'):

        paramkeys = format_spec.get('paramkeys')
        if paramkeys:
            s = ', '.join(dumps(v, paramkey=k, **format_spec) for v, k in zip(x, paramkeys))
        else:
            s = ', '.join(dumps(v, **format_spec) for v in x)

        if format_spec.get('parens'):
            s = '(%s)' % s
        return s

    if x is None:
        return 'null'

    return str(x)

class SQLTemplate(object):
    '''A SQL template.

    :param template_groups: the template groups
    :type template_groups: two-level nest iterable

    Here is an example of SQL's `select ...` statement:

    >>> select_tmpl = SQLTemplate(
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

    The example of changing the formating specification by its attribute:

    >>> tmpl = SQLTemplate(('key', '<value>'))
    >>> print tmpl.format(value='data')
    KEY data;
    >>> tmpl.param = True
    >>> print tmpl.param
    True
    >>> print tmpl.format(value='data')
    KEY %(data)s;

    .. seealso::
        The all of the formating specification: :py:func:`~sql.dumps`.

    If the formating specification isn't set, it raise a KeyError exception rather than an AttributeError:

    >>> print tmpl.x
    Traceback (most recent call last):
        ...
    KeyError: 'x'

    The formating specification is stored in the attribute, ``format_spec``:

    >>> print tmpl.format_spec
    {'param': True}

    If you want to know what fields it has, just print it.

    >>> print select_tmpl
    SQLTemplate(('select', '<select>'), ('from', '<table>'), ('where', '<where>'), ('group by', '<group_by>'), ('having', '<having>'), ('order by', '<order_by>'), ('limit', '<limit>'), ('offset', '<offset>'))
    '''

    def __init__(self, *template_groups):
        self.template_groups = template_groups
        self.format_spec = {}

    def __setattr__(self, key, value):
        if hasattr(self, 'format_spec'):
            self.format_spec[key] = value
        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        return object.__getattribute__(self, 'format_spec')[key]

    def format(self, **fields):
        '''Use keyword-arguments to format this template.

        :param fields: the fields you want to fill
        :type fields: dict
        '''
        return self.format_from_dict(fields)

    def format_from_dict(self, fields):
        '''Use dict to format this template.

        :param fields: the fields you want to fill
        :type fields: dict
        '''

        sql_components = []

        fields = fields.copy()

        for template_group in self.template_groups:

            # starts to render a template group
            rendered_templates = []
            for template in template_group:

                # if it need to be substitute
                if template.startswith('<'):

                    field_name = template[1:-1]
                    field_value = fields.get(field_name, Empty)
                    rendered = None

                    # handles special cases
                    # TODO: it could be abstracted as a parameter of initialization
                    if field_value is Empty:
                        if field_name == 'select':
                            rendered = '*'
                    else:
                        if field_name in ('where', 'having'):
                            rendered = dumps(field_value, condition=True, **self.format_spec)
                        elif field_name == 'set':
                            rendered = dumps(field_value, val=True, parens=True, **self.format_spec)
                        elif field_name == 'value_params':
                            rendered = dumps(field_value, val=True, parens=True, param=True, **self.format_spec)
                        elif field_name == 'multi_values':
                            rendered = dumps((dumps(i, val=True, parens=True, **self.format_spec) for i in field_value))
                        elif field_name == 'mapping':
                            fields['columns'], fields['values'] = zip(*field_value.items())
                        elif field_name == 'values':
                            rendered = dumps(field_value, val=True, parens=True, paramkeys=fields.get('columns'), **self.format_spec)
                        elif field_name == 'columns':
                            rendered = dumps(field_value, parens=True, **self.format_spec)
                        else:
                            rendered = dumps(field_value, **self.format_spec)

                    rendered_templates.append(rendered)
                else:
                    rendered_templates.append(template.upper())

            # all of the templates in a group must be rendered
            if all(rendered_templates):
                sql_components.append(' '.join(rendered_templates))

        return ' '.join(sql_components)+';'

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(repr(t) for t in self.template_groups)
        )

insert_tmpl = SQLTemplate(
    # The <mapping> could be a dict or iterable (prepared statement),
    # It will be disassembled into <columns> and <values>.
    ('<mapping>', ),
    # It is a template group, and
    # it only be rendered if every <field> is be filled.
    ('insert into', '<table>'),
    # It is another template group.
    ('<columns>', ),
    ('values', '<values>'),
    ('values', '<value_params>'),
    ('values', '<multi_values>'),
    ('returning', '<returning>'),
)

def insert(table, mapping=None, **fields):
    '''It is a shortcut for the SQL statement, ``insert into ...`` .

    :param table: the name of database's table
    :type table: str
    :param mapping: the data represented in a mapping
    :type mapping: mapping
    :param fields: the other fileds
    :type fields: mapping
    :rtype: :py:class:`str`

    The examples:

    >>> print insert('users', {'id': 'mosky'})
    INSERT INTO users (id) VALUES ('mosky');

    >>> print insert('users', {'id': ___ })
    INSERT INTO users (id) VALUES (%(id)s);

    >>> print insert('users', value_params=('id', 'name', 'email'))
    INSERT INTO users VALUES (%(id)s, %(name)s, %(email)s);

    >>> print insert('users', values=('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'))
    INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com');

    >>> print insert('users', columns=('email', 'id', 'name'), values=('mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu'))
    INSERT INTO users (email, id, name) VALUES ('mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu');

    >>> print insert('users', multi_values=(('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'), ('moskytw', 'Mosky Liu', 'mosky DOT liu AT pinkoi.com')))
    INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'), ('moskytw', 'Mosky Liu', 'mosky DOT liu AT pinkoi.com');

    The fields it has:

    >>> print insert_tmpl
    SQLTemplate(('<mapping>',), ('insert into', '<table>'), ('<columns>',), ('values', '<values>'), ('values', '<value_params>'), ('values', '<multi_values>'), ('returning', '<returning>'))

    The ``mapping`` is added by this libaray. It is for convenience and not a part of SQL.
    '''

    fields['table'] = table
    if mapping:
        fields['mapping'] = mapping
    return insert_tmpl.format_from_dict(fields)

select_tmpl = SQLTemplate(
    ('select', '<select>'),
    ('from', '<table>'),
    ('where', '<where>'),
    ('group by', '<group_by>'),
    ('having', '<having>'),
    ('order by', '<order_by>'),
    ('limit', '<limit>'),
    ('offset', '<offset>'),
)

def select(table, where=None, **fields):
    '''It is a shortcut for the SQL statement, ``select ...`` .

    :param table: the name of database's table
    :type table: str
    :param where: the conditions represented in a mapping
    :type where: mapping
    :param fields: the other fileds
    :type fields: mapping
    :rtype: :py:class:`str`

    The examples:

    >>> print select('users', {'id': 'mosky'})
    SELECT * FROM users WHERE id = 'mosky';

    >>> print select('users')
    SELECT * FROM users;

    >>> print select('users', order_by='id')
    SELECT * FROM users ORDER BY id;

    >>> print select('users', select='email', order_by=('email DESC', 'id'))
    SELECT email FROM users ORDER BY email DESC, id;

    >>> print select('users', {'id': ('mosky', 'moskytw')})
    SELECT * FROM users WHERE id IN ('mosky', 'moskytw');

    >>> print select('users', {'email like': '%@gmail.com'})
    SELECT * FROM users WHERE email LIKE '%@gmail.com';

    >>> print select('users', {'name': ___, 'email': 'mosky DOT tw AT gmail.com' })
    SELECT * FROM users WHERE name = %(name)s AND email = 'mosky DOT tw AT gmail.com';

    The fields it has:

    >>> print select_tmpl
    SQLTemplate(('select', '<select>'), ('from', '<table>'), ('where', '<where>'), ('group by', '<group_by>'), ('having', '<having>'), ('order by', '<order_by>'), ('limit', '<limit>'), ('offset', '<offset>'))
    '''

    fields['table'] = table
    if where:
        fields['where'] = where
    return select_tmpl.format_from_dict(fields)

update_tmpl = SQLTemplate(
    ('update', '<table>'),
    ('set', '<set>'),
    ('where', '<where>'),
    ('returning', '<returning>'),
)

def update(table, where=None, set=None, **fields):
    '''It is a shortcut for the SQL statement, ``update ...`` .

    :param table: the name of database's table
    :type table: str
    :param where: the conditions represented in a mapping
    :type where: mapping
    :param set: the part you want to update
    :type set: mapping
    :param fields: the other fileds
    :type fields: mapping
    :rtype: :py:class:`str`

    The examples:

    >>> print update('users', {'id': 'mosky'}, {'email': 'mosky DOT tw AT gmail.com'})
    UPDATE users SET email = 'mosky DOT tw AT gmail.com' WHERE id = 'mosky';

    >>> print update_tmpl
    SQLTemplate(('update', '<table>'), ('set', '<set>'), ('where', '<where>'), ('returning', '<returning>'))
    '''

    fields['table'] = table
    if where:
        fields['where'] = where
    if set:
        fields['set'] = set
    return update_tmpl.format_from_dict(fields)

delete_tmpl = SQLTemplate(
    ('delete from', '<table>'),
    ('where', '<where>'),
    ('returning', '<returning>'),#
)

def delete(table, where=None, **fields):
    '''It is a shortcut for the SQL statement, ``delete from ...`` .

    :param table: the name of database's table
    :type table: str
    :param where: the conditions represented in a mapping
    :type where: mapping
    :param fields: the other fileds
    :type fields: mapping
    :rtype: :py:class:`str`

    The examples:

    >>> print delete('users', {'id': 'mosky'})
    DELETE FROM users WHERE id = 'mosky';

    The fields it has:

    >>> print delete_tmpl
    SQLTemplate(('delete from', '<table>'), ('where', '<where>'), ('returning', '<returning>'))
    '''

    fields['table'] = table
    if where:
        fields['where'] = where
    return delete_tmpl.format_from_dict(fields)

def or_(*x, **format_spec):
    '''Concat expressions by operator, `OR`.

    The exmaples:

    >>> print or_("x = 'a'", 'y > 1')
    (x = 'a') OR (y > 1)

    >>> print or_({'x': 'a'}, {'y >': 1})
    (x = 'a') OR (y > 1)

    >>> str_exp = dumps({'x': 'a', 'y': 'b'}, condition=True)
    >>> print or_(str_exp, {'z': 'c', 't >': 0})
    (y = 'b' AND x = 'a') OR (t > 0 AND z = 'c')
    '''

    return ' OR '.join('(%s)' % dumps(i, condition=True, **format_spec) for i in x)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
