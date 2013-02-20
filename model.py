#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import MutableSequence, MutableMapping
import sql

#from psycopg2 import pool
#pool = pool.SimpleConnectionPool(1, 5, database='mosky')

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

    def __getitem__(self, col_idx_or_key):
        return self.model.elem(self.row_idx, col_idx_or_key)

    def __setitem__(self, col_idx_or_key, val):
        self.model.set_elem(self.row_idx, col_idx_or_key, val)

    def __delitem__(self, col_key):
        raise TypeError('use model.remove() instead')

    # --- implement standard mutable sequence ---

    def __repr__(self):
        return '<RowProxy for row %r: %r>' % (self.row_idx, dict(self))

    def cond(self):
        return dict((k, self[k]) for k in self.model.uni_col_names)

    def ident(self):
        return tuple(self[k] for k in self.model.uni_col_names)

class ColProxy(MutableSequence):

    def __init__(self, model, col_idx_or_key):
        self.model = model
        self.col_idx = self.model.to_col_idx(col_idx_or_key)

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

    # --- implement standard mutable sequence ---

    def __repr__(self):
        return '<ColProxy for col %r (%s): %r>' % (self.col_idx, self.model.col_names[self.col_idx], list(self))

class Model(MutableMapping):

    table = None
    col_names = tuple()
    uni_col_names = tuple()
    grp_col_names = tuple()

    def __init__(self, rows):

        if not hasattr(self, 'col_offsets'):
            self.__class__.col_offsets = dict((col_name, i) for i, col_name in enumerate(self.col_names))

        self.row_len = len(rows)
        self.col_len = len(self.col_names)

        self._elems = []
        for i, row in enumerate(rows):
            self._elems.extend(row)

        self.added_rows = []
        self.removed_row_conds = []
        self.changed_row_conds = {}
        self.changed_row_vals = {}

    def to_col_idx(self, col_idx_or_key):
        if isinstance(col_idx_or_key, basestring):
            return self.col_offsets[col_idx_or_key]
        else:
            return col_idx_or_key

    def to_col_name(self, col_idx_or_key):
        if isinstance(col_idx_or_key, (int, long)):
            return self.col_names[col_idx_or_key]
        else:
            return col_idx_or_key

    def to_elem_idx(self, row_idx, col_idx_or_key):
        return row_idx * self.col_len + self.to_col_idx(col_idx_or_key)

    # --- implement standard mutable sequence ---

    def __len__(self):
        return self.col_len

    def __iter__(self):
        for col_name in self.col_names:
            yield col_name

    def __getitem__(self, x):
        if isinstance(x, basestring):
            if x in self.grp_col_names:
                return self.elem(0, x)
            else:
                return self.col(x)
        elif isinstance(x, (int, long)):
            return self.row(x)

    def __setitem__(self, grp_col_name, val):
        if grp_col_name in self.grp_col_names:
            self.set_elem(0, grp_col_name, val)

    def __delitem__(self, x, val):
        pass

    # --- end ---

    def row(self, i):
        return RowProxy(self, i)

    def col(self, col_idx_or_key):
        return ColProxy(self, col_idx_or_key)

    def elem(self, row_idx, col_idx_or_key):
        return self._elems[self.to_elem_idx(row_idx, col_idx_or_key)]

    def rows(self):
        for i in xrange(self.row_len):
            yield self.row(i)

    def cols(self):
        for col_name in self.col_names:
            yield self.col(col_name)

    def set_elem(self, row_idx, col_idx_or_key, val):

        elem_idx = self.to_elem_idx(row_idx, col_idx_or_key)
        uni_col_vals = self[row_idx].ident()
        if uni_col_vals not in self.changed_row_conds:
            if col_idx_or_key in self.grp_col_names:
                self.changed_row_conds[uni_col_vals] = {col_idx_or_key: self._elems[elem_idx]}
            else:
                self.changed_row_conds[uni_col_vals] = self[row_idx].cond()

        self._elems[elem_idx] = val

        if uni_col_vals in self.changed_row_vals:
            self.changed_row_vals[uni_col_vals][self.to_col_name(col_idx_or_key)] = self._elems[elem_idx]
        else:
            self.changed_row_vals[uni_col_vals] = {self.to_col_name(col_idx_or_key): self._elems[elem_idx]}

    def add_row(self, row):
        self.added_rows.append(row)
        self._elems.extend(row)
        self.row_len += 1

    def remove_row(self, row_idx):
        self.removed_row_conds.append(self[row_idx].cond())
        self.row_len -= 1
        start = row_idx * self.col_len
        del self._elems[start:start+self.col_len]

    def commit(self):
        for row in self.added_rows:
            print sql.insert(self.table, self.col_names, row)
        for row_cond in self.removed_row_conds:
            print sql.delete(self.table, row_cond)
        for k in self.changed_row_conds:
            print sql.update(self.table, self.changed_row_conds[k], self.changed_row_vals[k])

if __name__ == '__main__':

    Model.table = 'user_details'
    Model.col_names = ('serial', 'user_id', 'email')
    Model.uni_col_names = set(['serial'])
    Model.grp_col_names = set(['user_id'])

    m = Model(
        [
            (0, 'moskytw', 'mosky.tw@typo.com'),
            (1, 'moskytw', 'mosky.liu@gmail.com'),
            (2, 'moskytw', '<It is not used anymore.>'),
        ]
    )

    print '* the model:'
    for col_name in m:
        print '%-7s:' % col_name, m[col_name]
    print

    print '* the 2nd row, and the values:'
    print m[1]
    for col_name, val in m[1].items():
        print '%-7s:' % col_name, val
    print

    print "* the 'email' column, and the values:"
    print m['email']
    print
    for i, email in enumerate(m['email']):
        print '%d:' % i, email
    print

    print '* fix the typo'
    m['email'][0] = 'mosky.tw@gmmail.com'
    m['email'][0] = 'mosky.tw@gmail.com'
    print m['email'][0]
    print

    ## NOTE: It is not recommended.
    #print '* modified unique column'
    #m[0]['serial'] = 10
    #print m[0]['serial']
    #print

    print "* a group column, 'user_id':"
    print m['user_id']
    print

    print "* modifiy the group column, 'user_id':"
    m['user_id'] = 'mosky'
    print 'modified:', m['user_id']
    print

    print '* remove the last row'
    m.remove_row(2)
    print 'row_len: ', m.row_len
    print

    print '* add a row'
    m.add_row((3, 'mosky', 'mosky@ubuntu-tw.org'))
    print 'row_len: ', m.row_len
    print

    print '* the model after above changes:'
    for col_name in m:
        print '%-7s:' % col_name, m[col_name]
    print

    print '* commit'
    m.commit()
    print
