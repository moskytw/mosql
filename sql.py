#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains useful functions to build SQL with common Python's data types.'''

# The default styles of ``dumps``
encoding   = 'UTF-8'
paramstyle = 'pyformat'
boolstyle  = 'uppercase'

# A hyper None, because None represents null in SQL.
Empty = ___ = type('Empty', (object, ), {
    '__nonzero__': lambda self: False,
    '__str__'    : lambda self: '___',
    '__repr__'   : lambda self: 'Empty',
})()

default = type('default', (object, ), {
    '__str__'   : lambda self: 'DEFAULT',
    '__repr__'   : lambda self: 'default',
})()


def escape(s):
    '''Replace the ``'`` (single quote) by ``''`` (two single quotes).

    :param s: a string which you want to escape
    :type s: str
    :rtype: str

    >>> print dumps("'DROP TABLE member; --", val=True)
    '\''DROP TABLE member; --'

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
    :type format_spec: dict

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
    ('a', 'b', 'c')

    Actually, you can use any `iterable` (except mapping) to build the above strings.

    The examples of `mapping`:

    >>> print dumps({'a': 1, 'b': 'str'})
    a = 1, b = 'str'

    >>> print dumps({'a >=': 1, 'b': ('x', 'y')}, condition=True)
    b IN ('x', 'y') AND a >= 1

    The examples of using ``param`` to build `prepared statement`:

    >>> print dumps(('a', 'b', 'c'), val=True, param=True)
    (%(a)s, %(b)s, %(c)s)

    >>> print dumps(('a', 'b', 'c'), val=True, param=True, paramstyle='qmark')
    (?, ?, ?)

    The `paramstyle` can be `pyformat`, `qmark`, `named` or `format_spec`. The `numberic` isn't supported yet.

    >>> print dumps({'a >=': 'a', 'b': 'b'}, param=True, condition=True)
    b = %(b)s AND a >= %(a)s

    The exmaples of using ``condition`` and iterable (not mapping) to build `prepared statement`:

    >>> print dumps(('x', 'y >', 'z <'), condition=True)
    x = %(x)s AND y > %(y)s AND z < %(z)s

    The examples of using :py:class:`Empty` object, ``___`` (triple-underscore) to build `prepared statement`:

    >>> print dumps({'a >=': 1, 'b': ___ }, condition=True)
    b = %(b)s AND a >= 1

    >>> print dumps({'a >=': ___ , 'b': ___ }, condition=True)
    b = %(b)s AND a >= %(a)s

    >>> print dumps((___, 'b', 'c'), val=True, autoparams=('x', 'y', 'z'))
    (%(x)s, 'b', 'c')
    '''

    global encoding, paramstyle, boolstyle, escape

    if isinstance(x, unicode):
        x = x.encode(format_spec.get('encoding', encoding))

    param = format_spec.get('param')
    autoparam = format_spec.get('autoparam')

    if x is Empty and autoparam:
        param = True
        x = dumps(autoparam)

    if param and isinstance(x, (str, int)):
        _paramstyle = format_spec.get('paramstyle', paramstyle)
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

    if x is None:
        return 'null'

    items = None
    if hasattr(x, 'items'):
        items = x.items()
    # convert iterable to items if ``condition`` or ``set`` is set
    elif hasattr(x, '__iter__') and (format_spec.get('condition') or format_spec.get('set')):
        format_spec['param'] = True
        items = ((v, splitop(v)[0]) for v in x)

    if items:

        operations = []
        for k, v in items:

            # find the operator in key
            k, op = splitop(k)
            if op is None:
                if not isinstance(v, basestring) and hasattr(v, '__iter__'):
                    op = 'in'
                else:
                    op = '='

            # update the format_spec for value
            v_format_spec = format_spec.copy()
            v_format_spec['autoparam'] = k
            v_format_spec['val'] = True
            v_format_spec['condition'] = False

            operations.append('%s %s %s' % (
                dumps(k),
                op.upper(),
                dumps(v, **v_format_spec),
            ))

        if format_spec.get('condition'):
            return ' AND '.join(operations)
        else:
            return ', '.join(operations)

    if hasattr(x, '__iter__'):

        sep = format_spec.get('sep')
        if sep:
            return sep.join(dumps(v, **format_spec) for v in x)

        autoparams = format_spec.get('autoparams')
        if autoparams:
            s = ', '.join(dumps(v, autoparam=k, **format_spec) for v, k in zip(x, autoparams))
        else:
            s = ', '.join(dumps(v, **format_spec) for v in x)

        if format_spec.get('val') or format_spec.get('parens'):
            s = '(%s)' % s
        return s

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
    KEY data
    >>> tmpl.param = True
    >>> print tmpl.param
    True
    >>> print tmpl.format(value='data')
    KEY %(data)s

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

                # if it need to be substituted
                if template.startswith('<'):

                    field_name = template[1:-1]
                    field_value = fields.get(field_name, Empty)
                    rendered = None

                    # handles the special cases
                    # TODO: it could be abstracted as a parameter of initialization
                    if field_value is Empty:
                        if field_name == 'select':
                            rendered = '*'
                    else:
                        if field_name in ('where', 'having'):
                            rendered = dumps(field_value, condition=True, **self.format_spec)
                        elif field_name == 'join':
                                rendered = dumps(field_value, sep=' ', **self.format_spec)
                        elif field_name == 'on':
                            rendered = dumps(field_value, sep=' AND ', **self.format_spec)
                        elif field_name == 'using':
                            if isinstance(field_value, basestring):
                                field_value = (field_value, )
                            rendered = dumps(field_value, parens=True, **self.format_spec)
                        elif field_name == 'type':
                                rendered = dumps(field_value).upper()
                        elif field_name == 'set':
                            rendered = dumps(field_value, set=True, **self.format_spec)
                        elif field_name == 'columns':

                            if isinstance(field_value, basestring):
                                rendered = dumps((field_value, ), parens=True, **self.format_spec)
                            elif hasattr(field_value, 'items'):
                                fields['columns'], fields['values'] = zip(*field_value.items())
                                rendered = dumps(fields['columns'], parens=True, **self.format_spec)
                            elif not fields.get('values') and hasattr(field_value, '__iter__'):
                                rendered = '%s VALUES %s' % (
                                    dumps(field_value, parens=True, **self.format_spec),
                                    dumps(field_value, val=True, param=True, **self.format_spec)
                                )
                            else:
                                rendered = dumps(field_value, parens=True, **self.format_spec)

                        elif field_name == 'values':

                            if isinstance(field_value, basestring):
                                rendered = dumps((field_value, ), parens=True, **self.format_spec)
                            # iterable but not strings
                            elif all(hasattr(i, '__iter__') and not isinstance(i, basestring) for i in field_value):
                                rendered = dumps((dumps(i, val=True, **self.format_spec) for i in field_value))
                            else:
                                rendered = dumps(field_value, val=True, autoparams=fields.get('columns'), **self.format_spec)
                        else:
                            # normal case
                            rendered = dumps(field_value, **self.format_spec)

                    rendered_templates.append(rendered)
                else:
                    rendered_templates.append(template.upper())

            # all of the templates in a group must be rendered
            if all(rendered_templates):
                sql_components.append(' '.join(rendered_templates))

        return ' '.join(sql_components)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(repr(t) for t in self.template_groups)
        )

insert_tmpl = SQLTemplate(
    # It is a template group, and
    # it only be rendered if every <field> is be filled.
    ('insert into', '<table>'),
    # It is another template group.
    ('<columns>', ),
    ('values'   , '<values>'),
    ('returning', '<returning>'),
)

def insert(table, columns=None, values=None, **fields):
    '''It is a shortcut for the SQL statement, ``insert into ...`` .

    :rtype: str

    The simple examples:

    >>> print insert('member', {'member_id': 'mosky'})
    INSERT INTO member (member_id) VALUES ('mosky')

    >>> print insert('member', ('email', 'member_id', 'name'), ('mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu'))
    INSERT INTO member (email, member_id, name) VALUES ('mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu')

    >>> print insert('member', "email, member_id, name", "'mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu'")
    INSERT INTO member (email, member_id, name) VALUES ('mosky DOT tw AT gmail.com', 'mosky', 'Mosky Liu')

    >>> print insert('member', values=('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'))
    INSERT INTO member VALUES ('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com')

    >>> print insert('post', {'post_id': default})
    INSERT INTO post (post_id) VALUES (DEFAULT)

    The exmaples of building `prepared statement`:

    >>> print insert('member', ('member_id', 'name', 'email'))
    INSERT INTO member (member_id, name, email) VALUES (%(member_id)s, %(name)s, %(email)s)

    >>> print insert('member', {'member_id': 'mosky', 'name': ___})
    INSERT INTO member (name, member_id) VALUES (%(name)s, 'mosky')

    An example of multi-value:

    >>> print insert('member', values=(('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'), ('moskytw', 'Mosky Liu', 'mosky DOT liu AT pinkoi.com')))
    INSERT INTO member VALUES ('mosky', 'Mosky Liu', 'mosky DOT tw AT gmail.com'), ('moskytw', 'Mosky Liu', 'mosky DOT liu AT pinkoi.com')

    All of the fields:

    >>> print insert_tmpl
    SQLTemplate(('insert into', '<table>'), ('<columns>',), ('values', '<values>'), ('returning', '<returning>'))
    '''

    fields['table'] = table
    if columns:
        fields['columns'] = columns
    if values:
        fields['values'] = values
    return insert_tmpl.format_from_dict(fields)

select_tmpl = SQLTemplate(
    ('select', '<select>'),
    ('from'  , '<table>'),
    ('where' , '<where>'),
    ('<join>', ),
    ('group by', '<group_by>'),
    ('having'  , '<having>'),
    ('order by', '<order_by>'),
    ('limit' , '<limit>'),
    ('offset', '<offset>'),
)

def select(table, where=None, select=None, **fields):
    '''It is a shortcut for the SQL statement, ``select ...`` .

    :rtype: str

    The simple examples:

    >>> print select('member')
    SELECT * FROM member

    >>> print select('member', {'name': 'Mosky Liu'}, ('member_id', 'name'), limit=10, order_by=('member_id', 'created DESC'))
    SELECT member_id, name FROM member WHERE name = 'Mosky Liu' ORDER BY member_id, created DESC LIMIT 10

    >>> print select('member', "name = 'Mosky Liu'", 'member_id, name', limit=10, order_by='member_id, created DESC')
    SELECT member_id, name FROM member WHERE name = 'Mosky Liu' ORDER BY member_id, created DESC LIMIT 10

    The exmaples which use the condition(s):

    >>> print select('member', {'member_id': ('mosky', 'moskytw')})
    SELECT * FROM member WHERE member_id IN ('mosky', 'moskytw')

    >>> print select('member', {'email like': '%@gmail.com'})
    SELECT * FROM member WHERE email LIKE '%@gmail.com'

    The examples of using `prepared statement`:

    >>> print select('member', ('name', 'email'))
    SELECT * FROM member WHERE name = %(name)s AND email = %(email)s

    >>> print select('member', {'name': ___, 'email': 'mosky DOT tw AT gmail.com' })
    SELECT * FROM member WHERE name = %(name)s AND email = 'mosky DOT tw AT gmail.com'

    The exmaples of using ``join``:

    >>> print select('table_x', join='NATUAL JOIN table_y')
    SELECT * FROM table_x NATUAL JOIN table_y

    >>> print select('table_x', join=('NATUAL JOIN table_y', 'NATUAL JOIN table_z'))
    SELECT * FROM table_x NATUAL JOIN table_y NATUAL JOIN table_z

    .. seealso::
        Here is a function helps you to build the `join` statement: :py:func:`~sql.join`.

    All of the fields:

    >>> print select_tmpl
    SQLTemplate(('select', '<select>'), ('from', '<table>'), ('where', '<where>'), ('<join>',), ('group by', '<group_by>'), ('having', '<having>'), ('order by', '<order_by>'), ('limit', '<limit>'), ('offset', '<offset>'))
    '''

    fields['table'] = table
    if where:
        fields['where'] = where
    if select:
        fields['select'] = select
    return select_tmpl.format_from_dict(fields)

join_tmpl = SQLTemplate(
    ('<type>', ),
    ('join'  , '<table>'),
    ('on'    , '<on>'),
    ('using' , '<using>'),
)

def join(table, on=None, using=None, type=None, **fields):
    '''It is a shortcut for the SQL statement, ``join ...`` .

    :param type: It can be 'cross', 'natural', 'inner', 'left' or 'right'.
    :type type: str
    :rtype: str

    Without giving ``type``, it determines type automatically. It uses `left` join by default:

    >>> print join('another', 'table.c1 = another.c1')
    LEFT JOIN another ON table.c1 = another.c1

    >>> print join('another', ('table.c1 = another.c1', 'table.c2 = another.c2'))
    LEFT JOIN another ON table.c1 = another.c1 AND table.c2 = another.c2

    >>> print join('table', using='c1')
    LEFT JOIN table USING (c1)

    >>> print join('table', using=('c1', 'c2'))
    LEFT JOIN table USING (c1, c2)

    But if you give ``table`` only, it will switch to `natural` join.

    >>> print join('table')
    NATURAL JOIN table

    All of the fields:

    >>> print join_tmpl
    SQLTemplate(('<type>',), ('join', '<table>'), ('on', '<on>'), ('using', '<using>'))

    .. seealso::
        :py:func:`~sql.cross`, :py:func:`~sql.natural`, :py:func:`~sql.inner`, :py:func:`~sql.left` and :py:func:`~sql.right`

    '''

    fields['table'] = table

    if on:
        fields['on'] = on
    if using:
        fields['using'] = using

    if type:
        fields['type'] = type
    else:
        if on or using:
            fields['type'] = 'left'
        else:
            fields['type'] = 'natural'

    return join_tmpl.format_from_dict(fields)

def cross(table):
    '''It is a shortcut for the SQL statement, ``cross join ...`` .

    :rtype: str

    >>> print cross('table')
    CROSS JOIN table
    '''
    return join(table, type='cross')

def natural(table):
    '''It is a shortcut for the SQL statement, ``natural join ...`` .

    :rtype: str

    >>> print natural('table')
    NATURAL JOIN table
    '''
    return join(table, type='natural')

def inner(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``inner join ...`` .

    :rtype: str

    >>> print inner('table', using='c1')
    INNER JOIN table USING (c1)
    '''
    return join(table, type='inner', on=on, using=using)

def left(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``left join ...`` .

    :rtype: str

    >>> print left('table', using='c1')
    LEFT JOIN table USING (c1)
    '''
    return join(table, type='left', on=on, using=using)

def right(table, on=None, using=None):
    '''It is a shortcut for the SQL statement, ``right join ...`` .

    :rtype: str

    >>> print right('table', using='c1')
    RIGHT JOIN table USING (c1)
    '''
    return join(table, type='right', on=on, using=using)

update_tmpl = SQLTemplate(
    ('update', '<table>'),
    ('set'   , '<set>'),
    ('where' , '<where>'),
    ('returning', '<returning>'),
)

def update(table, where=None, set=None, **fields):
    '''It is a shortcut for the SQL statement, ``update ...`` .

    :rtype: str

    >>> print update('member', {'member_id': 'mosky'}, {'email': 'mosky DOT tw AT gmail.com'})
    UPDATE member SET email = 'mosky DOT tw AT gmail.com' WHERE member_id = 'mosky'

    >>> print update('member', "member_id = 'mosky'", "email = 'mosky DOT tw AT gmail.com'")
    UPDATE member SET email = 'mosky DOT tw AT gmail.com' WHERE member_id = 'mosky'

    >>> print update('member', ('member_id', ), ('email', 'name'))
    UPDATE member SET email = %(email)s, name = %(name)s WHERE member_id = %(member_id)s

    All of the fields:

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
    ('where'    , '<where>'),
    ('returning', '<returning>'),
)

def delete(table, where=None, **fields):
    '''It is a shortcut for the SQL statement, ``delete from ...`` .

    :rtype: str

    >>> print delete('member', {'member_id': 'mosky'})
    DELETE FROM member WHERE member_id = 'mosky'

    >>> print delete('member', "member_id = 'mosky'")
    DELETE FROM member WHERE member_id = 'mosky'

    All of the fields:

    >>> print delete_tmpl
    SQLTemplate(('delete from', '<table>'), ('where', '<where>'), ('returning', '<returning>'))
    '''

    fields['table'] = table
    if where:
        fields['where'] = where
    return delete_tmpl.format_from_dict(fields)

def or_(*x, **format_spec):
    '''Concat expressions by operator, `OR`.

    :rtype: str

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
