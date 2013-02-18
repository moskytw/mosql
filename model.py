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
        if isinstance(idx, slice):
            return list(self.model[self.fixed_idx])[idx]
        else:
            return self.model.__getitem__((self.fixed_idx, idx))

    def __setitem__(self, idx, val):
        if isinstance(idx, slice):
            raise TypeError('seting item by slice is not supported yet: %r' % idx)
        else:
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

    table = None
    col_names = tuple()

    def __init__(self, rows):

        if not hasattr(self, 'col_offsets'):
            self.__class__.col_offsets = dict((col_name, i) for i, col_name in enumerate(self.col_names))

        self.col_len = len(self.col_names)

        self.elems = []
        for i, row in enumerate(rows):
            self.elems.extend(row)

        self.snapshot = rows

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

    def _to_slice(self, nidx):

        row, col = nidx
        if row is None:
            return slice(col, None, self.col_len)
        elif col is None:
            s = row*self.col_len
            return slice(s, s+self.col_len, None)
        else:
            return row*self.col_len+col

    def _is_to_squash_col(self, nidx):

        row, col = nidx

        # if the target of normalized index is a column
        if row is None and col is not None:
            # if user specified the squash_col_names
            if hasattr(self, 'squash_col_names'):
                return self.col_names[col] in self.squash_col_names
            # , or treats all of the column's index is unique column
            else:
                return True
        else:
            return False

    # --- implement standard mutable sequence ---

    def __len__(self):
        return len(self.elems) / self.col_len

    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]

    def __getitem__(self, idx):

        nidx = self._normalize_idx(idx)

        if self._is_to_squash_col(nidx):
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

    # --- simulate mapping's methods ---

    def keys(self):
        return list(self.col_names)

    def values(self):
        return [self[col_name] for col_name in self.col_names]

    def items(self):
        return [(col_name, self[col_name]) for col_name in self.col_names]

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    # --- end ---

    def add(self, row):
        self.elems.extend(row)

    def change(self, idx, val):

        nidx = self._normalize_idx(idx)

        if self._is_to_squash_col(nidx):
            val = (val, ) * len(self)

        self.elems[self._to_slice(nidx)] = val

    def remove(self, row_idx=None):

        if row_idx is None:
            for i in enumerate(self):
                self.remove(i)
        elif isinstance(row_idx, (int, long)):
            if row_idx >= len(self):
                raise ValueError('out of range')
            del self.elems[self._to_slice(self._normalize_idx(row_idx))]
        else:
            raise TypeError("'row_idx' must be int: %r" % row_idx)

    def commit(self):
        pass

if __name__ == '__main__':

    import sql

    Model.table = 'user_detail'
    Model.col_names = ('serial', 'user_id', 'email')
    Model.squash_col_names = set(['user_id'])

    m = Model(
        [
            (0, 'moskytw', 'mosky.tw@typo.com'),
            (1, 'moskytw', 'mosky.liu@gmail.com'),
            (2, 'moskytw', '<It is not used anymore.>'),
        ]
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
    #print 'changed:', m.changed
    print

    print "* print a unique col, 'user_id':"
    print m['user_id']
    print

    print "* change 'user_id':"
    m['user_id'] = 'mosky'
    print m['user_id']
    #print 'changed:', m.changed
    print

    print '* remove the last row'
    m.remove(2)
    #print 'deleted:', m.removed
    print

    print '* add a row'
    m.add((None, 'mosky', 'mosky@ubuntu-tw.org'))
    #print 'added:', m.added
    print

    print '* print the rows in the model again:'
    for i, row in enumerate(m):
        print '%d:' % i, row
    print

    m.commit()

    print '--- another model ---'
    print

    Model.col_names = ('user_id', 'name')
    del Model.squash_col_names
    del Model.col_offsets

    m = Model(
        [
            ('mosky', 'Mosky Liu'),
        ]
    )

    print '* print the rows in the model:'
    for i, row in enumerate(m):
        print '%d:' % i, row
    print

    print '* print the cols in the model:'
    for col_name in m.col_names:
        print '%-7s:' % col_name, m[col_name]
    print

    print "* test the mapping's methods"
    print 'keys  :', m.keys()
    print 'values:', m.values()
    print 'items :', m.items()
    print 'get   :', m.get('no exists', 'default value')
