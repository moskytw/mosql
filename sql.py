#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sql_operator import stringify, to_keyword

class SQL(dict):
    '''A SQL builder lets you use Python's syntax to build SQL.'''

    @classmethod
    def insert_into(cls, table):
        sql = cls()
        sql.order = ('insert into', 'values', 'returning')
        sql['insert into'] = table
        return sql

    @classmethod
    def select(cls, *fields):
        sql = cls()
        sql.order = ('select', 'from', 'where', 'order by', 'limit', 'offset', 'asc', 'desc')
        sql['select'] = fields
        return sql

    @classmethod
    def get(cls, table, *fields):
        sql = cls()
        sql.order = ('select', 'from', 'where', 'order by', 'limit', 'offset', 'asc', 'desc')
        sql['from'] = table
        sql['select'] = fields or '*'
        return sql

    @classmethod
    def update(cls, table):
        sql = cls()
        sql.order = ('update', 'set', 'from', 'where', 'returning')
        sql['update'] = table
        return sql

    @classmethod
    def delete_from(cls, table):
        sql = cls()
        sql.order = ('delete from', 'where', 'returning')
        sql['delete from'] = table
        return sql

    def __init__(self):
        object.__setattr__(self, 'order', tuple())

    def __getattr__(self, key):
        '''It makes clause functions.

        Examples:

            sql = SQL.delete_from(table).where("key='value'")
        '''

        keyword = to_keyword(key)
        if keyword in self.order:
            def setitem(*args):
                self[keyword] = args
                return self
            return setitem
        else:
            return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        '''It let you use attributes to access items (this class inherits the dict).

        Example:

            sql = SQL.delete_from(table)
            sql.where = "key='value'"
        '''

        keyword = to_keyword(key)
        if keyword in self.order:
            self[keyword] = value
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        '''It converts this object into a standard SQL query.'''

        sql_components = []
        for keyword in self.order:
            if keyword in self:
                sql_components.append(keyword.upper())
                stringified_value = stringify(self[keyword])
                if stringified_value: sql_components.append(stringified_value)

        return ' '.join(sql_components)

if __name__ == '__main__':

    from sql_operator import eq

    sql1 = SQL.insert_into('user')
    sql1.values_(repr(('mosky', 'Mosky Liu', 'moskytw@gmail.com')))
    print sql1
    # -> INSERT INTO user VALUES ('mosky', 'Mosky Liu', 'moskytw@gmail.com')

    sql2 = SQL.select('uid', 'name', 'email').from_('user').limit(1)
    sql2.where = eq('uid', 'mosky')
    print sql2
    # -> SELECT uid, name, email FROM user WHERE uid = 'mosky' LIMIT 1

    sql2['where'] = eq('email', 'mosky.tw@gmail.com')
    print sql2
    # -> SELECT uid, name, email FROM user WHERE email = 'mosky.tw@gmail.com' LIMIT 1

    sql3 = SQL.update('user').set(eq('email', 'mosky.tw@gmail.com')).where(eq('uid', 'mosky'))
    print sql3
    # -> UPDATE user SET email = 'mosky.tw@gmail.com' WHERE uid = 'mosky'

    sql4 = SQL.delete_from('user').where(eq('uid', 'mosky'))
    print sql4
    # -> DELETE FROM user WHERE uid = 'mosky'

    sql5 = SQL.get('user', 'uid', 'name', 'email')
    sql5.limit = 1
    print sql5
    # -> SELECT uid, name, email FROM user LIMIT 1

    sql6 = SQL.select('password').from_('shadow').where(eq('uid', "hacker' or 1=1; DROP TABLE user; --"))
    print sql6
    # -> SELECT password FROM shadow WHERE uid=''' or 1=1; DROP TABLE user; --'

    sql7 = SQL.select('password').from_('shadow').where(eq('uid'))
    print sql7
    # -> SELECT password FROM shadow WHERE uid=?
