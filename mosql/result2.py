#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby

def get_column_names(cursor):
    return [row_desc[0] for row_desc in cursor.description]

class Model(object):

    @classmethod
    def arrange_cursor(cls, cursor, arrange_by, **kargs):
        return cls.arrange(get_column_names(cursor), cursor.fetchall(), arrange_by, **kargs)

    @classmethod
    def arrange(cls, column_names, rows, arrange_by, **kargs):

        name_index_map = dict((name, i) for i, name  in enumerate(column_names))
        key_indexes = tuple(name_index_map[name] for name in arrange_by)
        key_func = lambda row: tuple(row[i] for i in key_indexes)

        for _, rows in groupby(rows, key_func):
            yield cls(column_names, list(rows))

    @classmethod
    def from_cursor(cls, cursor, **kargs):
        return cls(get_column_names(cursor), cursor.fetchall(), **kargs)

    def __init__(self, column_names, rows, **kargs):

        self.column_names = column_names

        self.columns = dict((name, [
            row[i] for row in rows
        ]) for i, name in enumerate(self.column_names))

        for k, v in kargs.items():
            setattr(self, k, v)

    def column(self, column_name):
        return self.columns[column_name]

    def __iter__(self):
        return (name for name in self.column_names)

    def row(self, row_index):
        return [self.column(column_name)[row_index] for column_name in self]

    def __getitem__(self, column_name):
        return self.column(column_name)

    def __setitem__(self, column_name, value):
        pass

    def __repr__(self):
        return repr(self.columns)

if __name__ == '__main__':

    import psycopg2

    conn = psycopg2.connect(database='mosky')
    cursor = conn.cursor()
    cursor.execute('select * from person')

    m = Model.from_cursor(cursor)
    print m.column_names
    print m.columns
    print m.column('person_id')
    print m.row(0)

    cursor.execute('select * from person')
    print list(Model.arrange_cursor(cursor, arrange_by=('person_id', )))

    cursor.close()
    conn.close()
