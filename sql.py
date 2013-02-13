#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains some useful funtions to build SQL with basic Python's data type.'''

encoding = 'UTF-8'
paramstyle = 'pyformat'

param_makers = {
    'pyformat': lambda k: '%%(%s)s' % k,
    'qmark'   : lambda k: '?',
    'named'   : lambda k: ':%s' % k,
    'format'  : lambda k: '%s',
    # 'numberic': lambda k: ':%d' % d, # TODO
}

def param_maker(k, paramstyle_=None):
    '''Retrun a parameter maker.

    If ``paramstyle_`` is not set, it will read global ``paramstyle``.'''
    return param_makers.get(paramstyle_ or paramstyle)(k)

# A hyper None, because None represent null in SQL.
Empty = type('Empty', (object,), {
    '__nonzero__': lambda self: False,
    '__repr__'   : lambda self: 'Empty',
})()

def dumps(x, quote=False, tuple=False, expression=False, paramstyle=None):
    '''Dump any object ``x`` into SQL's representation.

    It supports:

    - ``None`` (as ``null`` in SQL)
    - ``unicode``
    - number (includes ``int`` ,``float`` and ``long``)
    - ``dict``
    - iterable (includes ``tuple``, ``list``, ...)

    It returns None if it doesn't know how to convert.

    The additionally format arguments:

    - ``quote`` works on strings. It adds the single quotes around a string, and replaces single quote to two single quotes ('') in this string.
    - ``tuple`` works on iterable. It adds the parentheses around a stringified iterable.
    - ``expression`` works on dict. It will find the operator out from key, or automatically generate an operator by type of value.

    >>> print dumps(None)
    null

    >>> print dumps(123)
    123

    >>> print dumps('It is a string.')
    It is a string.

    >>> print dumps('It is a string.', quote=True)
    'It is a string.'

    >>> print dumps("' or 1=1 --", quote=True)
    '\'' or 1=1 --'

    >>> print dumps("' DROP TABLE users; --", quote=True)
    '\'' DROP TABLE users; --'

    >>> print dumps({'key': 'value'})
    key='value'

    >>> print dumps(('string', 123, 123.456))
    string, 123, 123.456

    >>> print dumps(('string', 123, 123.456), quote=True)
    'string', 123, 123.456

    >>> print dumps(('string', 123, 123.456), tuple=True)
    (string, 123, 123.456)

    >>> print dumps(('string', 123, 123.456), quote=True, tuple=True)
    ('string', 123, 123.456)

    >>> print dumps({'key': ('a', 'b')}, expression=True)
    key IN ('a', 'b')

    >>> print dumps({'created >': 0}, expression=True)
    created > 0

    >>> print dumps(('name', 'created >'), expression=True)
    name = %(name)s AND created > %(created)s
    '''

    if expression:

        items = None
        if hasattr(x, 'items'):
            is_param_maker = False
            items = x.items()
        elif hasattr(x, '__iter__'):
            items = ((k, Empty) for k in x)
        else:
            return dumps(x)

        strs = []
        for k, v in items:
            # find the expression out
            str_k = dumps(k, tuple=True).strip()
            # NOTE: It can't handle iterable or dict-like correctly.
            space_pos = str_k.rfind(' ')
            op = None
            if space_pos != -1:
                str_k, op = str_k[:space_pos], str_k[space_pos+1:]
            # if we can't find an expression
            if not op:
                if hasattr(v, '__iter__'):
                    op = 'in'
                else:
                    op = '='
            # use parameter maker if `v` is Empty
            if v is Empty:
                str_v = param_maker(str_k, paramstyle)
            else:
                str_v = dumps(v, quote=True, tuple=True)

            strs.append('%s %s %s' % (str_k, op.upper(), str_v))

        return ' AND '.join(strs)

    if x is None:
        return 'null'

    if isinstance(x, (int, float, long)):
        return str(x)

    if isinstance(x, unicode):
        x = x.encode(encoding)

    if isinstance(x, str):
        s = x
        if quote:
            s = "'%s'" % s.replace("'", "''")
        return s
    if hasattr(x, 'items'):
        return  ', '.join('%s=%s' % (dumps(k), dumps(v, quote=True, tuple=True)) for k, v in x.items())

    if hasattr(x, '__iter__'):
        s = ', '.join(dumps(i, quote, tuple) for i in x)
        if tuple:
            return '(%s)' % s
        else:
            return s

class SQL(object):
    '''It builds a SQL statement by given template.

    An example of `select ...` statement:

    >>> sql = SQL(
    ...     # It is a template group, and
    ...     # it only be rendered if every <field> is be filled.
    ...     ('select', '<select>'),
    ...     # It is another template group.
    ...     ('from', '<table>'),
    ...     ('where', '<where>'),
    ...     ('group by', '<groupby>'),
    ...     ('having', '<having>'),
    ...     ('order by', '<orderby>'),
    ...     ('limit', '<limit>'),
    ...     ('offset', '<offset>'),
    ... )

    And use attribute ``field_names`` to get the field names:

    >>> sql.field_names == set(
    ...     ['select', 'table', 'where', 'groupby', 'having', 'orderby', 'limit', 'offset']
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
        self.paramstyle = None

    def update(self, dict):
        '''Use a dict to update the fields' values.'''
        self.filled.update(dict)

    def __setattr__(self, key, value):
        '''It supports to use attribute to update field.

        >>> sql = SQL(('field', '<field>'))
        >>> sql.field = {'id': 'mosky.tw@gmail.com'}
        >>> print sql
        FIELD id='mosky.tw@gmail.com';
        '''

        field_names = getattr(self, 'field_names', None)
        if field_names and key in field_names:
            self.filled[key] = value
            self.cached = None
        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        '''It supports to use attribute to get value of field.

        >>> sql = SQL(('field', '<field>'))
        >>> sql.field = {'id': 'mosky.tw@gmail.com'}

        >>> print sql.field
        {'id': 'mosky.tw@gmail.com'}

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

                    # handles special cases
                    # TODO: it could be abstracted as a parameter of initialization
                    if value is Empty:
                        if key == 'select':
                            value = '*'
                    else:
                        if key in ('where', 'having'):
                            value = dumps(value, expression=True, paramstyle=self.paramstyle)
                        elif key == 'values':
                            value = dumps(value, quote=True, tuple=True)
                        elif key == 'columns':
                            value = dumps(value, tuple=True)
                        else:
                            value = dumps(value)

                    rendered_templates.append(value)
                else:
                    rendered_templates.append(template.upper())

            # all of the templates in a group must be rendered
            if all(rendered_templates):
                sql_components.append(' '.join(rendered_templates))

        self.cached = ' '.join(sql_components)+';'
        return self.cached

def insert(table, **fields):
    '''Return a `SQL` instance of SQL statement ``insert into ...``.

    >>> print insert('users', values=('mosky', 'Mosky Liu', 'mosky.tw@gmail.com'))
    INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky.tw@gmail.com');

    >>> print insert('users', columns=('email', 'id', 'name'), values=('mosky.tw@gmail.com', 'mosky', 'Mosky Liu'))
    INSERT INTO users (email, id, name) VALUES ('mosky.tw@gmail.com', 'mosky', 'Mosky Liu');

    >>> print insert('users').field_names == set(
    ...     ['table', 'values', 'columns', 'returning']
    ... )
    True
    '''

    sql = SQL(
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
    '''Return a `SQL` instance of SQL statement ``select ...``.

    >>> print select('users')
    SELECT * FROM users;

    >>> print select('users', orderby='id')
    SELECT * FROM users ORDER BY id;

    >>> print select('users', select='id', orderby=('id DESC', 'email'))
    SELECT id FROM users ORDER BY id DESC, email;

    >>> print select('users', limit=1, where={'id': 'mosky'})
    SELECT * FROM users WHERE id = 'mosky' LIMIT 1;

    >>> print select('users', where={'id': ('mosky', 'moskytw')})
    SELECT * FROM users WHERE id IN ('mosky', 'moskytw');

    >>> print select('users', where={'email like': '%@gmail.com'})
    SELECT * FROM users WHERE email LIKE '%@gmail.com';

    >>> print select('users', where=('name', 'email'))
    SELECT * FROM users WHERE name = %(name)s AND email = %(email)s;

    >>> sql = select('users', where=('name', 'email'))
    >>> sql.paramstyle = 'qmark'
    >>> print sql
    SELECT * FROM users WHERE name = ? AND email = ?;

    >>> print select('users').field_names == set(
    ...     ['select', 'table', 'where', 'groupby', 'having', 'orderby', 'limit', 'offset']
    ... )
    True
    '''

    sql = SQL(
        ('select', '<select>'),
        ('from', '<table>'),
        ('where', '<where>'),
        ('group by', '<groupby>'),
        ('having', '<having>'),
        ('order by', '<orderby>'),
        ('limit', '<limit>'),
        ('offset', '<offset>'),
    )
    fields['table'] = table
    sql.update(fields)
    return sql

def update(table, **fields):
    '''Return a `SQL` instance of SQL statement ``update ...``.

    >>> print update('users', set={'email': 'mosky.tw@gmail.com'}, where={'id': 'mosky'})
    UPDATE users SET email='mosky.tw@gmail.com' WHERE id = 'mosky';

    >>> print update('users').field_names == set(
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
    '''Return a `SQL` instance of SQL statement ``delete from ...``.

    >>> print delete('users', where={'id': 'mosky'})
    DELETE FROM users WHERE id = 'mosky';

    >>> print delete('users').field_names == set(
    ...     ['table', 'where', 'returning']
    ... )
    True
    '''

    sql = SQL(
        ('delete from', '<table>'),
        ('where', '<where>'),
        ('returning', '<returning>'),
    )
    sql.filled['table'] = table
    sql.filled.update(fields)
    return sql

if __name__ == '__main__':
    import doctest
    doctest.testmod()
