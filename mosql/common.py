#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It contains the builders of common SQL statement.'''

__all__ = ['insert', 'select', 'update', 'delete', 'insert_tmpl', 'select_tmpl', 'update_tmpl', 'delete_tmpl']

from .util import ___, default, SQLTemplate

insert_tmpl = SQLTemplate(
    # It is a template group, and
    # it only be rendered if every <field> is filled.
    ('insert into', '<table>'),
    # It is another template group.
    ('<columns>', ),
    ('values'   , '<values>'),
    ('returning', '<returning>'),
)
'''The template for :py:func:`mosql.common.insert`.'''

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
    ('<join>', ),
    ('where' , '<where>'),
    ('group by', '<group_by>'),
    ('having'  , '<having>'),
    ('order by', '<order_by>'),
    ('limit' , '<limit>'),
    ('offset', '<offset>'),
)
'''The template for :py:func:`mosql.common.select`.'''

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
        Here is a function helps you to build the `join` statement: :py:func:`mosql.ext.join`.

    All of the fields:

    >>> print select_tmpl
    SQLTemplate(('select', '<select>'), ('from', '<table>'), ('<join>',), ('where', '<where>'), ('group by', '<group_by>'), ('having', '<having>'), ('order by', '<order_by>'), ('limit', '<limit>'), ('offset', '<offset>'))
    '''

    fields['table'] = table
    if where:
        fields['where'] = where
    if select:
        fields['select'] = select
    return select_tmpl.format_from_dict(fields)

update_tmpl = SQLTemplate(
    ('update', '<table>'),
    ('set'   , '<set>'),
    ('where' , '<where>'),
    ('returning', '<returning>'),
)
'''The template for :py:func:`mosql.common.update`.'''

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
'''The template for :py:func:`mosql.common.delete`.'''

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
