#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby

from . import common as sql

def get_column_names(cursor):
    return [row_desc[0] for row_desc in cursor.description]

class Model(object):

    squashed = set()

    # --- methods which handle connection ---

    @classmethod
    def getconn(cls):
        raise NotImplementedError('This method should return a connection.')

    @classmethod
    def putconn(cls, conn):
        raise NotImplementedError('This method should accept a connection.')

    def perform(self, sql_or_sqls):

        conn = self.getconn()
        cur = conn.cursor()

        if isinstance(sql_or_sqls, basestring):
            sqls = [sql_or_sqls]
        else:
            sqls = sql_or_sqls

        try:
            cur.execute('; '.join(sqls))
        except:
            conn.rollback()
            raise
        else:
            conn.commit()

        self.putconn(conn)

        return cur

    # --- methods which load data into a model or models ---

    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def load_rows(self, column_names, rows):

        self.column_names = column_names

        self.columns = dict((name, [
            row[i] for row in rows
        ]) for i, name in enumerate(self.column_names))

    @classmethod
    def from_rows(self, column_names, rows, **attrs):
        m = cls(attrs)
        m.load_rows(column_names, rows)
        return m

    def load_cursor(self, cursor):
        self.load_rows(get_column_names(cursor), cursor.fetchall())

    @classmethod
    def from_cursor(cls, cursor, **attrs):
        m = cls(**attrs)
        m.load_cursor(cursor)
        return m

    @classmethod
    def arrange_rows(cls, column_names, rows, arrange_by, **attrs):

        name_index_map = dict((name, i) for i, name  in enumerate(column_names))
        key_indexes = tuple(name_index_map[name] for name in arrange_by)
        key_func = lambda row: tuple(row[i] for i in key_indexes)

        for _, rows in groupby(rows, key_func):
            m = cls(**attrs)
            m.load_rows(column_names, list(rows))
            yield m

    @classmethod
    def arrange_cursor(cls, cursor, arrange_by, **attrs):
        return cls.arrange_rows(get_column_names(cursor), cursor.fetchall(), arrange_by, **attrs)

    # --- methods which help you access model ---

    def column(self, column_name):
        return self.columns[column_name]

    def __iter__(self):
        return (name for name in self.column_names)

    def row(self, row_index):
        return [self.columns[column_name][row_index] for column_name in self]

    def __getitem__(self, column_name):
        if column_name in self.squashed:
            return self.columns[column_name][0]
        else:
            return self.columns[column_name]

    def __setitem__(self, column_name, value):
        pass

    def __repr__(self):
        return repr(dict((k, self[k]) for k in self))

if __name__ == '__main__':

    import psycopg2

    conn = psycopg2.connect(database='mosky')
    cursor = conn.cursor()
    cursor.execute('select * from person')

    m = Model.from_cursor(cursor)
    print m
    print m.column_names
    print m.columns
    print m['person_id']
    print m['name']
    print m.column('person_id')
    print m.row(0)
    print

    from pprint import pprint

    cursor.execute('select * from person')
    ms = list(
        Model.arrange_cursor(
            cursor,
            arrange_by = ('person_id', ),
            squashed   = set(['person_id', 'name'])
        )
    )
    pprint(ms)
    print

    m = ms[0]
    print m
    print m.column_names
    print m.columns
    print m['person_id']
    print m['name']
    print m.column('person_id')
    print m.row(0)
    print

    cursor.close()
    conn.close()

    m.getconn = lambda: psycopg2.connect(database='mosky')
    m.putconn = lambda conn: None
    for row in m.perform('select * from person'):
        print row
