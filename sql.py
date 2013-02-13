#!/usr/bin/env python
# -*- coding: utf-8 -*-

def quoted(s):
    '''Add single quotes around ``s`` and replace the single quote (') to double quotes ('') in ``s``.

    >>> print quoted('string without single quote')
    'string without single quote'

    >>> print quoted("' or 1=1 --")
    '\'' or 1=1 --'

    >>> print quoted("' DROP TABLE users; --")
    '\'' DROP TABLE users; --'
    '''
    return "'%s'" % s.replace("'", "''")

ENCODING = 'UTF-8'

def stringify(x, quote=False, tuple=False):
    '''Convert any object ``x`` to SQL's representation.

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

    >>> print stringify(None)
    null

    >>> print stringify(123)
    123

    >>> print stringify('It is a string.')
    It is a string.

    >>> print stringify('It is a string.', quote=True)
    'It is a string.'

    >>> print stringify({'key': 'value'})
    key='value'

    >>> print stringify(('string', 123, 123.456))
    string, 123, 123.456

    >>> print stringify(('string', 123, 123.456), quote=True)
    'string', 123, 123.456

    >>> print stringify(('string', 123, 123.456), tuple=True)
    (string, 123, 123.456)

    >>> print stringify(('string', 123, 123.456), quote=True, tuple=True)
    ('string', 123, 123.456)

    >>> print stringify({'key': 'value'}, quote=True)
    key='value'
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
            s = quoted(x)
        return s

    if hasattr(x, 'items'):
        return ', '.join('%s=%s' % (stringify(k), stringify(v, quote=True, tuple=True)) for k, v in x.items())

    if hasattr(x, '__iter__'):
        s = ', '.join(stringify(i, quote, tuple) for i in x)
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

    @classmethod
    def insert(cls, table, **kargs):
        '''A SQL builder for ``insert into`` statement.

        >>> print SQL.insert('users', values=('mosky', 'Mosky Liu', 'mosky.tw@gmail.com'))
        INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky.tw@gmail.com');

        >>> print SQL.insert('users', columns=('id', 'name', 'email'), values=('mosky', 'Mosky Liu', 'mosky.tw@gmail.com'))
        INSERT INTO users (id, name, email) VALUES ('mosky', 'Mosky Liu', 'mosky.tw@gmail.com');
        '''

        sql = cls(
            # It is a template group, and
            # it only be rendered if every <field> is be filled.
            ('insert into', '<table>'),
            # It is another template group.
            ('<columns>', ),
            ('values', '<values>'),
            ('returning', '<returning>'),
        )
        sql.filled['table'] = table
        sql.filled.update(kargs)
        return sql

    @classmethod
    def select(cls, table, **kargs):
        '''A SQL builder for ``select`` statement.

        >>> print SQL.select('users')
        SELECT * FROM users;

        >>> print SQL.select('users', limit=1, where={'id': 'mosky'})
        SELECT * FROM users WHERE id='mosky' LIMIT 1;

        >>> print SQL.select('users', select=('id', 'email'), order_by='id', desc=True)
        SELECT id, email FROM users ORDER BY id DESC;
        '''

        sql = cls(
            ('select', '<select>'),
            ('from', '<table>'),
            ('where', '<where>'),
            ('group by', '<group by>'),
            ('having', '<having>'),
            ('order by', '<order_by>'),
            ('<asc>', ),
            ('<desc>', ),
            ('limit', '<limit>'),
            ('offset', '<offset>'),
        )
        sql.filled['table'] = table
        sql.filled.update(kargs)
        return sql

    @classmethod
    def update(cls, table, **kargs):
        '''A SQL builder for ``update`` statement.

        >>> print SQL.update('users', set={'email': 'mosky.tw@gmail.com'}, where={'id': 'mosky'})
        UPDATE users SET email='mosky.tw@gmail.com' WHERE id='mosky';
        '''

        sql = cls(
            ('update', '<table>'),
            ('set', '<set>'),
            ('where', '<where>'),
            ('returning', '<returning>'),
        )
        sql.filled['table'] = table
        sql.filled.update(kargs)
        return sql

    @classmethod
    def delete(cls, table, **kargs):
        '''A SQL builder for ``delete from`` statement.

        >>> print SQL.delete('users', where={'id': 'mosky'})
        DELETE FROM users WHERE id='mosky';
        '''

        sql = cls(
            ('delete from', '<table>'),
            ('where', '<where>'),
            ('returning', '<returning>'),
        )
        sql.filled['table'] = table
        sql.filled.update(kargs)
        return sql

    def __init__(self, *template_groups):
        self.template_groups = template_groups
        self.field_names = set()
        for template_group in template_groups:
            for template in template_group:
                if template.startswith('<'):
                    self.field_names.add(template[1:-1])
        self.filled = {}
        self.cached = None

    def __setattr__(self, key, value):
        '''
        >>> sql = SQL.select('users')
        >>> print sql
        SELECT * FROM users;
        >>> sql.where = {'id': 'mosky.tw@gmail.com'}
        >>> print sql
        SELECT * FROM users WHERE id='mosky.tw@gmail.com';
        '''
        field_names = getattr(self, 'field_names', None)
        if field_names and key in field_names:
            self.filled[key] = value
            self.cached = None
        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        '''
        >>> sql = SQL.select('users', where={'id': 'mosky.tw@gmail.com'})
        >>> sql.where
        {'id': 'mosky.tw@gmail.com'}
        >>> sql.x
        Traceback (most recent call last):
            ...
        KeyError: 'x'
        '''
        field_names = object.__getattribute__(self, 'field_names')
        return self.filled[key]

    def __str__(self):

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
                    elif key == 'desc' and value:
                        value = 'DESC'
                    elif key == 'asc' and value:
                        value = 'ASC'
                    elif key == 'values':
                        value = stringify(value, quote=True, tuple=True)
                    elif key == 'columns':
                        value = stringify(value, tuple=True)
                    else:
                        value = stringify(value)

                    rendered_templates.append(value)
                else:
                    rendered_templates.append(template.upper())

            # all of the templates in a group must be rendered
            if all(rendered_templates):
                sql_components.append(' '.join(rendered_templates))

        self.cached = ' '.join(sql_components)+';'
        return self.cached

if __name__ == '__main__':
    import doctest
    doctest.testmod()
