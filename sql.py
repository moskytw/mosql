#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains some useful funtions to build SQL with basic Python's data type.'''

ENCODING = 'UTF-8'

def dumps(x, quote=False, tuple=False, operator=False):
    '''Dump any object ``x`` to SQL's representation.

    It supports:

    - ``None`` (as ``null`` in SQL)
    - ``unicode``
    - number (include ``int`` and ``float``)
    - ``dict``
    - iterable (include ``tuple``, ``list``, ...)

    It returns None if it doesn't know how to convert.

    The additionally format arguments:

    - ``quote`` works on strings. It adds the single quotes around a string, and replaces single quote to two single quotes ('') in this string.
    - ``tuple`` works on iterable. It adds the parentheses around a stringified iterable.
    - ``operator`` works on dict. It will find the operator out from key, or automatically generate an operator by type of value.

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

    >>> print dumps({'key': ('a', 'b')}, operator=True)
    key IN ('a', 'b')

    >>> print dumps({'time >': 0}, operator=True)
    time > 0
    '''

    if x is None:
        return 'null'

    if isinstance(x, (int, float, long)):
        return str(x)

    if isinstance(x, unicode):
        x = x.encode(ENCODING)

    if isinstance(x, str):
        s = x
        if quote:
            s = "'%s'" % s.replace("'", "''")
        return s

    if hasattr(x, 'items'):
        if operator:
            strs = []
            for k, v in x.items():
                # find the operator out
                str_k = dumps(k).strip()
                space_pos = str_k.rfind(' ')
                op = None
                if space_pos != -1:
                    str_k, op = str_k[:space_pos], str_k[space_pos+1:]
                # if we can't find an operator
                if not op:
                    if hasattr(v, '__iter__'):
                        op = 'in'
                    else:
                        op = '='
                strs.append('%s %s %s' % (str_k, op.upper(), dumps(v, quote=True, tuple=True)))
            return ' AND '.join(strs)
        else:
            return  ', '.join('%s=%s' % (dumps(k), dumps(v, quote=True, tuple=True)) for k, v in x.items())

    if hasattr(x, '__iter__'):
        s = ', '.join(dumps(i, quote, tuple) for i in x)
        if tuple:
            return '(%s)' % s
        else:
            return s

# A hyper None, because None represent null in SQL.
Empty = type('Empty', (object,), {
    '__nonzero__': lambda self: False,
    '__repr__'   : lambda self: 'Empty',
})()

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
    ...     ('group by', '<group_by>'),
    ...     ('having', '<having>'),
    ...     ('order by', '<order_by>'),
    ...     ('<asc>', ),
    ...     ('<desc>', ),
    ...     ('limit', '<limit>'),
    ...     ('offset', '<offset>'),
    ... )

    And use attribute ``field_names`` to get the field names:

    >>> sql.field_names == set(
    ...     ['select', 'table', 'where', 'group_by', 'having', 'order_by', 'asc', 'desc', 'limit', 'offset']
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
                    if key == 'select' and not value:
                        value = '*'
                    elif key in ('where', 'having'):
                        value = dumps(value, operator=True)
                    elif key == 'desc' and value:
                        value = 'DESC'
                    elif key == 'asc' and value:
                        value = 'ASC'
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

    >>> print select('users', order_by='id', desc=True)
    SELECT * FROM users ORDER BY id DESC;

    >>> print select('users', select='id', order_by=('id', 'email'), desc=True)
    SELECT id FROM users ORDER BY id, email DESC;

    >>> print select('users', limit=1, where={'id': 'mosky'})
    SELECT * FROM users WHERE id = 'mosky' LIMIT 1;

    >>> print select('users', where={'id': ('mosky', 'moskytw')})
    SELECT * FROM users WHERE id IN ('mosky', 'moskytw');

    >>> print select('users', where={'email like': '%@gmail.com'})
    SELECT * FROM users WHERE email LIKE '%@gmail.com';

    >>> print select('users').field_names == set(
    ...     ['select', 'table', 'where', 'group_by', 'having', 'order_by', 'asc', 'desc', 'limit', 'offset']
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
        ('<asc>', ),
        ('<desc>', ),
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
