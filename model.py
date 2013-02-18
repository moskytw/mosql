#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import MutableSequence

#from psycopg2 import pool
#pool = pool.SimpleConnectionPool(1, 5, database='mosky')

class Proxy(MutableSequence):

    def __init__(self, model, fixed_idx):
        self.model = model
        self.fixed_idx = fixed_idx

    # --- implement standard mutable sequence ---

    def __len__(self):
        row, col = self.model._normalize_idx(self.fixed_idx)
        if row is None:
            return len(self.model)
        elif col is None:
            return self.model.col_len

    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]

    def __getitem__(self, idx):
        return self.model.__getitem__((self.fixed_idx, idx))

    def __setitem__(self, idx, val):
        self.model.__setitem__((self.fixed_idx, idx), val)

    def __delitem__(self, idx):
        raise TypeError('use model.remove() instead')

    def insert(self, idx, val):
        raise TypeError('use model.add() instead')

    # --- implement standard mutable sequence ---

    def __str__(self):
        return '%r' % list(self)

    def __repr__(self):
        return '<proxy at 0x%x for model %r. fixed_idx=%r>' % (id(self), self.model, self.fixed_idx)

class Model(MutableSequence):

    col_names = ('serial', 'user_id', 'email')
    uni_col_names = set(['user_id'])

    def __init__(self, rows, col_names=None):

        if col_names:
            self.col_names = col_names
            self.col_offsets = dict((k, i) for i, k in enumerate(col_names))
        elif not hasattr(self.__class__, 'col_offsets'):
            self.__class__.col_offsets = dict((k, i) for i, k in enumerate(self.col_names))

        self.col_len = len(self.col_names)

        self.elems = []
        for i, row in enumerate(rows):
            self.elems.extend(row)

        self.changed = {}
        self.removed = []
        self.added = []

    def _normalize_idx(self, idx):

        if isinstance(idx, basestring):
            return (None, self.col_offsets[idx])

        elif isinstance(idx, int):
            return (idx, None)

        if hasattr(idx, '__iter__') and len(idx) == 2:
            row, col = idx
            if isinstance(row, basestring):
                col, row = row, col
            if isinstance(col, basestring):
                col = self.col_offsets[col]
            return (row, col)

        raise TypeError("type of 'idx' is not supported: %r" % idx)

    def _to_slice(self, idx):

        row, col = idx

        if row is None:
            return slice(col, None, self.col_len)
        elif col is None:
            s = row*self.col_len
            return slice(s, s+self.col_len, None)
        else:
            return row*self.col_len+col

    # --- implement standard mutable sequence ---

    def __len__(self):
        return len(self.elems) / self.col_len

    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]

    def __getitem__(self, idx):
        if idx in self.uni_col_names:
            return self.elems[self._to_slice(self._normalize_idx((0, idx)))]
        else:
            s = self._to_slice(self._normalize_idx(idx))
            if isinstance(s, slice):
                return Proxy(self, idx)
            else:
                return self.elems[s]

    def __setitem__(self, idx, val):
        self.change(idx, val)

    def __delitem__(self, row_idx):
        self.remove(row_idx)

    def insert(self, idx, val):
        raise TypeError('use model.add() instead')

    # --- end ---

    def add(self, row):
        self.elems.extend(row)
        self.added.append(row)

    def change(self, idx, val):

        nidx = self._normalize_idx(idx)

        if nidx not in self.changed:
            self.changed[nidx] = self[idx]

        if idx in self.uni_col_names:
            val = (val, ) * len(self)

        self.elems[self._to_slice(nidx)] = val

    def remove(self, row_idx):
        if isinstance(row_idx, (int, long)):
            s = self._to_slice(self._normalize_idx(row_idx))
            self.removed.append(self.elems[s])
            del self.elems[s]
        else:
            raise TypeError("'row_idx' must be int: %r" % row_idx)

if __name__ == '__main__':

    import sql

    m = Model(
        [
            (0, 'moskytw', 'mosky.tw@typo.com'),
            (1, 'moskytw', 'mosky.liu@gmail.com'),
            (2, 'moskytw', '<It is not used anymore.>'),
        ],
        ('serial', 'user_id', 'email')
    )

    print '* print the rows in the model:'
    for i, row in enumerate(m):
        print '%d:' % i, row
    print

    print '* print the 2nd row and the values in this row:'
    print m[1]
    print 'repr:', repr(m[1])
    print
    for i, val in enumerate(m[1]):
        print '%d:' % i, val
    print

    print "* print the 'email' col and the values in this row:"
    print m['email']
    print 'repr :', repr(m['email'])
    print
    for i, email in enumerate(m['email']):
        print '%d:' % i, email
    print

    print '* fix the typo'
    m['email', 0] = 'mosky.tw@gmmail.com'
    m['email'][0] = 'mosky.tw@gmail.com'
    print m['email']
    print 'changed:', m.changed
    print

    print "* print a unique col, 'user_id':"
    print m['user_id']
    print

    print "* change 'user_id':"
    m['user_id'] = 'mosky'
    print m['user_id']
    print 'changed:', m.changed
    print

    print '* remove the last row'
    m.remove(2)
    print 'deleted:', m.removed
    try:
        del m[2]
    except TypeError, e:
        print 'catch: %r' % e
    print

    print '* add a row'
    m.add((None, 'mosky', 'mosky@ubuntu-tw.org'))
    print 'added:', m.added
    print

    print '* print the rows in the model again:'
    for i, row in enumerate(m):
        print '%d:' % i, row
    print
