#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby, izip
from collections import defaultdict
import psycopg2
import sql

class Column(list):

    def __init__(self, model, name, x):
        list.__init__(self, x)
        self.model = model
        self.name = name

    def __setitem__(self, idx, x):
        self.model.set(self.name, idx, x)

    def __delitem__(self, idx):
        raise TypeError("this operation is not supported'")

    def append(self, x):
        raise TypeError("this operation is not supported'")

    def pop(self, x):
        raise TypeError("this operation is not supported'")

class ModelMeta(type):

    def __new__(meta, name, bases, attrs):

        Model = super(ModelMeta, meta).__new__(meta, name, bases, attrs)

        if Model.group is None:
            Model.group = Model.columns

        if Model.identity is None:
            Model.identity = Model.columns

        if Model.columns:

            Model.offsets = dict((k, i) for i, k in enumerate(Model.columns))
            Model.group_idxs = tuple(Model.offsets[k] for k in Model.group)
            Model.group_set = set(Model.group)
            Model.identity_idxs = tuple(Model.offsets[k] for k in Model.identity)

        return Model

class Model(dict):

    __metaclass__ = ModelMeta

    table    = None
    columns  = None
    group    = None
    identity = None

    @classmethod
    def arrange(cls, rows):

        keyfunc = lambda row: tuple(row[i] for i in cls.group_idxs)
        for grouped_vals, rows in groupby(rows, keyfunc):
            yield cls(rows)

    def __init__(self, rows):

        self.changes = defaultdict(dict)

        rows = list(rows)

        # TODO: It should be updated after saving
        self.identity_vals = [tuple(row[i] for i in self.identity_idxs) for row in rows]

        for name, col in izip(self.columns, izip(*rows)):
            if name in self.group_set:
                self[name] = col[0]
            else:
                self[name] = Column(self, name, col)

    def add(self, **row_vals):

        # auto fill group columns
        for k in self.group:
            if k not in row_vals:
                row_vals[k] = self[k]

        # update the columns
        for k in self.columns:
            # TODO: the default value must be DEFAULT in SQL
            v = row_vals.get(k)
            if k in self.group_set:
                self[k] = v
            else:
                list.append(self[k], v)

        self.changes.update({len(self.changes): row_vals})

    def set(self, col_name, row_idx, val):
        list.__setitem__(self[col_name], row_idx, val)
        self.changes.update(((self.identity_vals[row_idx], {col_name: val}), ))

    def remove(self, row_idx):

        for k in self.columns:
            if k in self.group_set:
                pass
            else:
                list.pop(self[k], row_idx)

        self.changes.update({self.identity_vals[row_idx]: None})

    def save(self):
        # TODO: It is just a rough draft
        for identity_vals, vals in self.changes.items():
            if isinstance(identity_vals, int):
                print sql.insert(self.table, vals)
            elif vals is None:
                print sql.delete(self.table, dict(zip(self.identity, identity_vals)))
            else:
                print sql.update(self.table, dict(zip(self.identity, identity_vals)), vals)
        # TODO: get the default value if there has any DEFAULT (may use returning?)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super(Model, self).__repr__())

class User(Model):
    table = 'user'
    columns = ('user_id', 'name')
    identity = ('user_id', )

class Detail(Model):
    table = 'detail'
    columns = ('detail_id', 'user_id', 'key', 'val')
    group = ('user_id', 'key')
    identity = ('detail_id', )

if __name__ == '__main__':

    from pprint import pprint

    conn = psycopg2.connect(database='mosky')
    cur = conn.cursor()

    cur.execute('select * from users order by user_id')
    for rows in User.arrange(cur.fetchall()):
        pprint(rows)
    print

    cur.execute('select * from details order by user_id, key, detail_id')
    for rows in Detail.arrange(cur.fetchall()):
        pprint(rows)
    print

    cur.execute("select * from details where user_id='mosky' and key='email' order by detail_id")
    detail = list(Detail.arrange(cur.fetchall()))[0]
    print detail
    detail['val'][0] = "rarely used"
    print detail
    detail.remove(1)
    print detail
    detail.add(val='mosky.tw@gmail.com')
    print detail
    print

    detail.save()

    conn.close()
