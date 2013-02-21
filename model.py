#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict, MutableSequence, MutableMapping
from itertools import groupby
import sql

class RowProxy(MutableMapping):

    def __init__(self, model, row_idx):
        self.model = model
        self.row_idx = row_idx

    # --- implement standard mutable sequence ---

    def __len__(self):
        return self.model.col_len

    def __iter__(self):
        for col_name in self.model.col_names:
            yield col_name

    def __getitem__(self, col_idx_or_name):
        return self.model.elem(self.row_idx, col_idx_or_name)

    def __setitem__(self, col_idx_or_name, val):
        self.model.set_elem(self.row_idx, col_idx_or_name, val)

    def __delitem__(self, col_name):
        raise TypeError('use model.remove() instead')

    # --- end ---

    def __repr__(self):
        return '<RowProxy for row %r: %r>' % (self.row_idx, dict(self))

    def cond(self):
        return dict((k, self[k]) for k in self.model.uni_col_names)

    def ident(self):
        return tuple(self[k] for k in self.model.uni_col_names)

class ColProxy(MutableSequence):

    def __init__(self, model, col_idx_or_name):
        self.model = model
        self.col_idx = self.model.to_col_idx(col_idx_or_name)

    # --- implement standard mutable sequence ---

    def __len__(self):
        return self.model.row_len

    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]

    def __getitem__(self, row_idx):
        return self.model.elem(row_idx, self.col_idx)

    def __setitem__(self, row_idx, val):
        self.model.set_elem(row_idx, self.col_idx, val)

    def __delitem__(self, row_idx):
        raise TypeError('use model.remove() instead')

    def insert(self, row_idx, val):
        raise TypeError('use model.add() instead')

    # --- end ---

    def __repr__(self):
        return '<ColProxy for col %r (%s): %r>' % (self.col_idx, self.model.col_names[self.col_idx], list(self))

class Model(MutableMapping):

    table = None
    col_names = tuple()
    uni_col_names = tuple()
    grp_col_names = tuple()
    ord_col_names = tuple()

    def __init__(self, grp_col=None):

        if not hasattr(self, 'col_offsets'):
            self.__class__.col_offsets = dict((col_name, i) for i, col_name in enumerate(self.col_names))

        if grp_col:
            self.grp_col_vals = dict(zip(self.grp_col_names, grp_col))
        self._elems = []

        self.col_len = len(self.col_names)
        self.row_len = 0

        self.added_rows = []
        self.removed_row_conds = []
        self.changed_row_conds = {}
        self.changed_row_vals = defaultdict(dict)
        self.changed_order = []

    def load(self, rows):

        for i, row in enumerate(rows):
            self._elems.extend(row)

        self.col_len = len(self.col_names)
        self.row_len = len(self._elems) / self.col_len

    @classmethod
    def find(cls, **where):
        model = cls()
        cur = cls.execute(sql=sql.select(cls.table, where, cls.col_names, order_by=cls.grp_col_names+cls.ord_col_names))
        rows = cur.fetchall()
        if not rows:
            return None
        elif not cls.grp_col_names or all(grp_col_name in where for grp_col_name in cls.grp_col_names):
            model = cls()
            model.load(rows)
            return model
        else:
            grp_col_idxs = map(model.to_col_idx, cls.grp_col_names)
            to_key = lambda row: map(row.__getitem__, grp_col_idxs)
            models = []
            for key, grouped_rows in groupby(rows, key=to_key):
                print key
                model = cls(key)
                model.load(grouped_rows)
                models.append(model)
            return models

    def to_col_idx(self, col_idx_or_name):
        if isinstance(col_idx_or_name, basestring):
            return self.col_offsets[col_idx_or_name]
        else:
            return col_idx_or_name

    def to_col_name(self, col_idx_or_name):
        if isinstance(col_idx_or_name, (int, long)):
            return self.col_names[col_idx_or_name]
        else:
            return col_idx_or_name

    def to_elem_idx(self, row_idx, col_idx_or_name):
        return row_idx * self.col_len + self.to_col_idx(col_idx_or_name)

    # --- implement standard mutable sequence ---

    def __len__(self):
        return self.col_len

    def __iter__(self):
        for col_name in self.col_names:
            yield col_name

    def __getitem__(self, x):
        if isinstance(x, basestring):
            if x in self.grp_col_names:
                return self.grp_col_vals.get(x)
            else:
                return self.col(x)
        elif isinstance(x, (int, long)):
            return self.row(x)

    def __setitem__(self, grp_col_name, val):
        if grp_col_name not in self.grp_col_names: return

        elem_idx = self.to_elem_idx(0, grp_col_name)

        if grp_col_name not in self.changed_row_conds:
            self.changed_row_conds[grp_col_name] = {grp_col_name: self._elems[elem_idx]}
            self.changed_order.append(grp_col_name)
        self.changed_row_vals[grp_col_name][grp_col_name] = val

        self.grp_col_vals[grp_col_name] = val

    def __delitem__(self, x, val):
        pass

    # --- end ---

    def row(self, i):
        return RowProxy(self, i)

    def col(self, col_idx_or_name):
        return ColProxy(self, col_idx_or_name)

    def elem(self, row_idx, col_idx_or_name):
        return self._elems[self.to_elem_idx(row_idx, col_idx_or_name)]

    def rows(self):
        for i in xrange(self.row_len):
            yield self.row(i)

    def cols(self):
        for col_name in self.col_names:
            yield self.col(col_name)

    def set_elem(self, row_idx, col_idx_or_name, val):

        row = self[row_idx]
        col_idx   = self.to_col_idx(col_idx_or_name)
        col_name  = self.to_col_name(col_idx_or_name)
        row_ident = row.ident()

        if row_ident not in self.changed_row_conds:
            self.changed_row_conds[row_ident] = row.cond()
            self.changed_order.append(row_ident)

        self.changed_row_vals[row_ident][col_name] = val
        self._elems[self.to_elem_idx(row_idx, col_idx_or_name)] = val

    def add(self, **vals):
        vals.update(self.grp_col_vals)
        row = [None] * self.col_len
        for col_name, offset in self.col_offsets.items():
            row[offset] = vals[col_name]
        self.add_row(row)

    def add_row(self, row):
        self.added_rows.append(row)
        self._elems.extend(row)
        self.row_len += 1

    def remove_row(self, row_idx):
        self.removed_row_conds.append(self[row_idx].cond())
        self.row_len -= 1
        start = row_idx * self.col_len
        del self._elems[start:start+self.col_len]

    @staticmethod
    def execute(self, sql=None, sqls=None):
        if sql:
            print sql
        if sqls:
            for sql in sqls:
                print sql

    def commit(self):
        sqls = []
        for row in self.added_rows:
            sqls.append(sql.insert(self.table, self.col_names, row))
        for row_cond in self.removed_row_conds:
            sqls.append(self.execute(sql.delete(self.table, row_cond)))
        for k in self.changed_order:
            sqls.append(sql.update(self.table, self.changed_row_conds[k], self.changed_row_vals[k]))
        self.execute(sqls=sqls)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict(self))

from psycopg2 import pool
pool = pool.SimpleConnectionPool(1, 5, database='mosky')

class PostgreSQLModel(Model):

    @staticmethod
    def execute(sql=None, sqls=None):
        conn = pool.getconn()
        cur = conn.cursor()
        if sql:
            print sql
            cur.execute(sql)
        if sqls:
            for sql in sqls:
                print sql
                cur.execute(sql)
        conn.commit()
        conn = pool.putconn(conn)
        return cur

class User(PostgreSQLModel):

    table = 'users'
    col_names = ('user_id', 'name')
    uni_col_names = ('user_id', )

class Detail(PostgreSQLModel):

    table = 'details'
    col_names = ('detail_id', 'user_id', 'key', 'val')
    uni_col_names = ('detail_id', )
    grp_col_names = ('user_id', 'key')
    ord_col_names = ('detail_id', )

if __name__ == '__main__':

    from pprint import pprint

    details = Detail.find(user_id='mosky')
    for detail in details:
        print detail

    detail = details[1]
    print detail
    detail['key'] = 'emails'
    detail['val'][0] = 'test@gmail.com'
    detail.commit()

    #detail = Detail(('mosky', 'email'))
    #detail.add(detail_id=11, val='newmail@mosky.tw')
    #detail.commit()

    user = User.find(user_id='mosky')
    print user
