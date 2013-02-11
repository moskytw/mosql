#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SQL(dict):
    '''A SQL builder lets you use Python's syntax to build SQL.'''

    @staticmethod
    def to_keyword(key):
        '''It converts the attribute name to the SQL keyword.

        Examples:

            from_    -> form
            order_by -> order by
            values_  -> values
        '''
        return key.replace('_', ' ').rstrip()

    @classmethod
    def flat(cls, obj):
        '''It flats an object.

        Examples:

            'str'      -> 'str'
            1          -> '1'
            ('x', 'y') -> 'x, y'
            callable   -> flat(callable())
        '''

        if isinstance(obj, basestring):
            return obj
        elif isinstance(obj, (int, float, long)):
            return str(obj)
        elif hasattr(obj, '__iter__'):
            return ', '.join(cls.flat(item) for item in obj)
        elif callable(obj):
            return self.flat(obj())

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

        keyword = self.to_keyword(key)
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

        keyword = self.to_keyword(key)
        if keyword in self.order:
            self[keyword] = value
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        '''It converts this object into a standard SQL query.'''

        flated_sql = []
        for keyword in self.order:
            if keyword in self:
                flated_sql.append(keyword.upper())
                flated_value = self.flat(self[keyword])
                if flated_value: flated_sql.append(flated_value)

        return ' '.join(flated_sql)

if __name__ == '__main__':

    def eq(key, value):
        return "%s='%s'" % (key, value)

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
