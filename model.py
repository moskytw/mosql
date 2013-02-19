#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import MutableSequence

#from psycopg2 import pool
#pool = pool.SimpleConnectionPool(1, 5, database='mosky')

class Proxy(MutableSequence):

    def __init__(self, model, fixed_idx):
        self.model = model
        self.fixed_idx = fixed_idx

        ridx, cidx = self.model._normalize_idx(self.fixed_idx)
        if ridx is None:
            self._len = lambda: len(self.model)
        elif cidx is None:
            self._len = lambda: self.model.col_len

    # --- implement standard mutable sequence ---

    def __len__(self):
        return self._len()

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
    columns = tuple()

    def __init__(self, rows):

        if not hasattr(self, 'col_offsets'):
            self.__class__.col_offsets = dict((col_name, i) for i, col_name in enumerate(self.columns))

        self.col_len = len(self.columns)

        self.elems = []
        for i, row in enumerate(rows):
            self.elems.extend(row)

        self.added_rows = []
        self.removed_row_conds = []
        self.changed_row_conds = {}
        self.changed_row_vals = {}

    def _normalize_idx(self, idx):

        if isinstance(idx, basestring):
            return (None, self.col_offsets[idx])

        elif isinstance(idx, int):
            return (idx, None)

        if hasattr(idx, '__iter__') and len(idx) == 2:
            ridx, cidx = idx
            if isinstance(ridx, basestring):
                cidx, ridx = ridx, cidx
            if isinstance(cidx, basestring):
                cidx = self.col_offsets[cidx]
            return (ridx, cidx)

        raise TypeError("type of 'idx' is not supported: %r" % idx)

    def _to_slice(self, nidx):

        # TODO: merge the slices

        ridx, cidx = nidx
        if ridx is None:
            return slice(cidx, None, self.col_len)
        elif cidx is None:
            s = ridx*self.col_len
            return slice(s, s+self.col_len, None)
        else:
            return ridx*self.col_len+cidx

    def _is_to_grp_col(self, nidx):

        ridx, cidx = nidx

        # if the target of normalized index is a cidxumn
        if ridx is None and cidx is not None:
            # if user specified the grp_columns
            if hasattr(self, 'grp_columns'):
                return self.columns[cidx] in self.grp_columns
            # , or treats all of the cidxumn's index is unique cidxumn
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

        if self._is_to_grp_col(nidx):
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
        return list(self.columns)

    def values(self):
        return [self[col_name] for col_name in self.columns]

    def items(self):
        return [(col_name, self[col_name]) for col_name in self.columns]

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    # --- end ---

    def _pick(self, row_idx, columns=None, only_keys=False):

        if only_keys:
            picked_columns = getattr(self, 'key_columns', None) or self.columns
        elif columns is None:
            picked_columns = self.columns

        row = self[row_idx]

        return dict((k, row[k]) for k in picked_columns)

    def add(self, row):
        self.elems.extend(row)
        self.added_rows.append(row)

    def change(self, idx, val):

        nidx = self._normalize_idx(idx)

        if self._is_to_grp_col(nidx):
            vals = self.changed_row_vals.setdefault(self.columns[nidx[1]], {})
            vals.update({self.columns[nidx[1]]: val})
            conds = self.changed_row_conds.setdefault(self.columns[nidx[1]], {})
            if not conds:
                conds.update({self.columns[nidx[1]]: self[self.columns[nidx[1]]]})
            val = (val, ) * len(self)
        else:
            vals = self.changed_row_vals.setdefault(nidx[0], {})
            vals.update({self.columns[nidx[1]]: val})
            conds = self.changed_row_conds.setdefault(nidx[0], {})
            if not conds:
                conds.update(self._pick(nidx[0], only_keys=True))

        self.elems[self._to_slice(nidx)] = val

    def remove(self, row_idx=None):

        if row_idx is None:
            for i in enumerate(self):
                self.remove(i)
        elif isinstance(row_idx, (int, long)):
            if row_idx >= len(self):
                raise ValueError('out of range')
            else:
                self.removed_row_conds.append(self._pick(row_idx, only_keys=True))
                del self.elems[self._to_slice(self._normalize_idx(row_idx))]
        else:
            raise TypeError("'row_idx' must be int: %r" % row_idx)

    def commit(self):
        for row in self.added_rows:
            print sql.insert(self.table, self.columns, row)
        print self.removed_row_conds
        for cond in self.removed_row_conds:
            print sql.delete(self.table, cond)
        for row_idx in self.changed_row_conds:
            print sql.update(self.table, self.changed_row_conds[row_idx], self.changed_row_vals[row_idx])

if __name__ == '__main__':

    import sql

    Model.table = 'user_details'
    Model.columns = ('serial', 'user_id', 'email')
    Model.key_columns = set(['serial'])
    Model.grp_columns = set(['user_id'])

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
    print

    print '* modified key'
    m[0, 'serial'] = 10
    print m[0]['serial']

    print "* print a unique col, 'user_id':"
    print m['user_id']
    print

    print "* change 'user_id':"
    m['user_id'] = 'mosky'
    print m['user_id']
    print

    print '* remove the last row'
    m.remove(2)
    print

    print '* add a row'
    m.add((None, 'mosky', 'mosky@ubuntu-tw.org'))
    print

    print '* print the rows in the model again:'
    for i, row in enumerate(m):
        print '%d:' % i, row
    print

    m.commit()

    print '--- another model ---'
    print

    Model.columns = ('user_id', 'name')
    del Model.grp_columns
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
    for col_name in m.columns:
        print '%-7s:' % col_name, m[col_name]
    print

    print "* test the mapping's methods"
    print 'keys  :', m.keys()
    print 'values:', m.values()
    print 'items :', m.items()
    print 'get   :', m.get('no exists', 'default value')
