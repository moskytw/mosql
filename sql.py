#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains some useful funtions to build SQL with basic Python's data type.'''

encoding = 'UTF-8'
paramstyle = 'pyformat'

param_markers = {
    'pyformat': lambda k: '%%(%s)s' % k,
    'qmark'   : lambda k: '?',
    'named'   : lambda k: ':%s' % k,
    'format'  : lambda k: '%s',
    # 'numberic': lambda k: ':%d' % d, # TODO
}

def param_marker(k, paramstyle_=None):
    '''Retrun a parameter marker.

    If ``paramstyle_`` is not set, it will read global ``paramstyle``.'''
    return param_markers.get(paramstyle_ or paramstyle)(k)

# A hyper None, because None represents null in SQL.
Empty = type('Empty', (object,), {
    '__nonzero__': lambda self: False,
    '__repr__'   : lambda self: 'Empty',
})()

def dumps(x, param=False, value=False, tuple=False, operator=False, paramstyle=None):
    '''Dump any object ``x`` into SQL's representation.

    The basic types:

    >>> print dumps(None)
    null

    >>> print dumps(123)
    123

    >>> print dumps('It is a string.')
    It is a string.

    >>> print dumps('It is a string.', value=True)
    'It is a string.'

    >>> print dumps("' or 1=1 --", value=True)
    '\'' or 1=1 --'

    >>> print dumps("' DROP TABLE users; --", value=True)
    '\'' DROP TABLE users; --'

    >>> print dumps('key', param=True)
    %(key)s

    >>> dumps('key', param=True) == dumps('key', param=True, value=True)
    True

    >>> print dumps('key', param=True, paramstyle='named')
    :key

    >>> print dumps('key', param=True, paramstyle='qmark')
    ?

    The tuple (represents iterable):

    >>> print dumps(('string', 123, 123.456))
    string, 123, 123.456

    >>> print dumps(('string', 123, 123.456), tuple=True)
    (string, 123, 123.456)

    >>> print dumps(('string', 123, 123.456), value=True, tuple=True)
    ('string', 123, 123.456)

    >>> print dumps(('key1', 'key2'), param=True, tuple=True)
    (%(key1)s, %(key2)s)

    >>> print dumps(('key1', 'key2'), param=True, tuple=True, operator=True)
    key2 = %(key2)s AND key1 = %(key1)s

    The dict-like (has `items` method):

    >>> print dumps({'key': 'value'})
    key='value'

    >>> print dumps({'key': 'value'}, operator=True)
    key = 'value'

    >>> print dumps({'key': ('value1', 'value2')}, operator=True)
    key IN ('value1', 'value2')

    >>> print dumps({'key like': '%alu%'}, operator=True)
    key LIKE '%alu%'

    >>> print dumps({'key': 'key'}, param=True, operator=True)
    key = %(key)s
    '''

    # basic types

    if x is None:
        return 'null'

    if isinstance(x, (int, float, long)):
        return str(x)

    if isinstance(x, unicode):
        x = x.encode(encoding)

    if isinstance(x, str):
        s = x
        if param:
            s = param_marker(s, paramstyle)
        elif value:
            # NOTE: In MySQL, it can't ensure the security if MySQL doesn't run in ANSI mode.
            s = "'%s'" % s.replace("'", "''")
        return s

    # dict-like
    if hasattr(x, 'items'):
        if operator:
            expressions = []
            for k, v in x.items():

                # k must be a basestring
                assert isinstance(k, basestring), 'left operand must be a string: %r' % k

                # try to find operator out
                op = None
                str_k = dumps(k)
                space_pos = str_k.rfind(' ')
                if space_pos != -1:
                    str_k, op = str_k[:space_pos], str_k[space_pos+1:]

                # if user doesn't give operator, generate an operator automatically
                if not op:
                    if hasattr(v, '__iter__'):
                        op = 'in'
                    else:
                        op = '='

                # render expression
                expressions.append('%s %s %s' % (str_k, op.upper(), dumps(v, param=param, value=True, tuple=True, operator=False, paramstyle=paramstyle)))

            return ' AND '.join(expressions)
        else:
            return  ', '.join('%s=%s' % (dumps(k), dumps(v, param=param, value=True, tuple=tuple, operator=False, paramstyle=paramstyle)) for k, v in x.items())

    # iterable
    if hasattr(x, '__iter__'):
        if operator:
            return dumps(dict((k, k) for k in x), param=param, value=value, tuple=tuple, operator=True, paramstyle=paramstyle)
        else:
            s = ', '.join(dumps(i, tuple=tuple, value=value, param=param, operator=operator, paramstyle=paramstyle) for i in x)
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

        values_param = False
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
                            value = dumps(value, param=(not hasattr(value, 'items')), operator=True, paramstyle=self.paramstyle)
                        elif key == 'pairs':
                            if hasattr(value, 'items'):
                                self.filled['columns'], self.filled['values'] = zip(*value.items())
                            elif hasattr(value, '__iter__'):
                                self.filled['columns'] = value
                                self.filled['values'] = value
                                values_param = True
                            value = None
                        elif key == 'values':
                            value = dumps(value, param=values_param, value=True, tuple=True)
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

    >>> print insert('users', pairs={'id': 'mosky'})
    INSERT INTO users (id) VALUES ('mosky');

    >>> print insert('users', pairs=('id', ))
    INSERT INTO users (id) VALUES (%(id)s);

    >>> print insert('users', values=('mosky', 'Mosky Liu', 'mosky.tw@gmail.com'))
    INSERT INTO users VALUES ('mosky', 'Mosky Liu', 'mosky.tw@gmail.com');

    >>> print insert('users', columns=('email', 'id', 'name'), values=('mosky.tw@gmail.com', 'mosky', 'Mosky Liu'))
    INSERT INTO users (email, id, name) VALUES ('mosky.tw@gmail.com', 'mosky', 'Mosky Liu');

    >>> print insert('users').field_names == set(
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
    fields['table'] = table
    sql.update(fields)
    return sql

if __name__ == '__main__':
    import doctest
    doctest.testmod()
