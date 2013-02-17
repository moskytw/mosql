#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Sequence

#from psycopg2 import pool
#pool = pool.SimpleConnectionPool(1, 5, database='mosky')

class Proxy(Sequence):

    def __init__(self, model, const, is_row):

        self.model = model
        self.const = const

        if is_row:
            self._transform = lambda i: self.const*self.model.col_len+i
            self._len = lambda: self.model.col_len
        else:
            self._transform = lambda i: i*self.model.col_len+self.const
            self._len = lambda: len(self.model)

    # --- implement standard sequence ---

    def __len__(self):
        return self._len()

    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]

    def __getitem__(self, i):

        if isinstance(i, slice):
            return [self[i] for i in xrange(*i.indices(len(self)))]

        return self.model.elems[self._transform(i)]

    # --- end ---

    def __setitem__(self, i, v):

        # XXX: it is confusing

        #if isinstance(i, slice):
        #    # TODO: check the two lengths are match
        #    from itertools import izip_longest
        #    for i, v in izip_longest(xrange(*i.indices(len(self))), v):
        #        self[i] = v
        #    return

        assert not isinstance(i, slice), 'using slice to assign values is not supported'

        self.model._update_elem(self._transform(i), v)

    def __str__(self):
        return '<Proxy for: %r>' % list(self)

class Model(Sequence):

    col_names = ('serial', 'user_id', 'email')
    uni_col_names = set(['user_id'])

    def __init__(self, rows, col_names=None):

        self.col_names = col_names = col_names or self.col_names

        self.col_len = len(col_names)
        self.col_offsets = dict((k, i) for i, k in enumerate(col_names))

        self.row_proxies = []
        self.col_proxies = {}
        self.elems = []

        for i, row in enumerate(rows):
            self.elems.extend(row)
            self.row_proxies.append(Proxy(self, i, is_row=True))

        for i, col_name in enumerate(col_names):
            self.col_proxies[col_name] = Proxy(self, i, is_row=False)

        self.updated = {}
        self.deleted = []
        self.inserted = []

    # --- implement standard sequence ---

    def __len__(self):
        return len(self.elems) / self.col_len

    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]

    def __getitem__(self, k):
        if k in self.uni_col_names:
            return self.elems[self.col_offsets[k]]
        else:
            if isinstance(k, basestring):
                return self.col_proxies[k]
            elif isinstance(k, (int, long)):
                return self.row_proxies[k]

    # --- end ---

    def _update_elem(self, i, v):
        if i not in self.updated:
            self.updated[i] = self.elems[i]
        self.elems[i] = v

    def __setitem__(self, k, v):
        assert k in self.uni_col_names, "k must be an unique column: %r" % k
        #self.elems[self.col_offsets[k]::self.col_len] = (v, ) * len(self)
        for i in xrange(*slice(self.col_offsets[k], None, self.col_len).indices(len(self.elems))):
            self._update_elem(i, v)

    def __delitem__(self, r):

        # remove the elems
        o = r * self.col_len
        s = slice(o, o+self.col_len)
        self.deleted.append(self.elems[s])
        del self.elems[s]

        # modified the proxies
        del self.row_proxies[r]
        for i in xrange(r, len(self)):
            self.row_proxies[i].const -= 1

    def add_row(self, r):
        self.row_proxies.append(Proxy(self, len(self), is_row=True))
        self.elems.extend(r)
        self.inserted.append(r)

    def as_dict(self, r):
        # TODO: add a dict proxy
        return dict((k, v) for k, v in zip(self.col_names, self[r]))

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
        print '%d:' % i, row, m.as_dict(i)
    print

    print '* print the 2nd row and the values in this row:'
    print m[1]
    for i, val in enumerate(m[1]):
        print '%d:' % i, val
    print

    print "* print the 'email' col and the values in this row:"
    print m['email']
    for i, email in enumerate(m['email']):
        print '%d:' % i, email
    print

    print '* fix the typo'
    m['email'][0] = 'mosky.tw@gmmail.com'
    m['email'][0] = 'mosky.tw@gmail.com'
    print m['email']
    print 'updated:', m.updated
    print

    print "* print a unique col, 'user_id':"
    print m['user_id']
    print

    print "* change 'user_id':"
    m['user_id'] = 'mosky'
    print m['user_id']
    print 'updated:', m.updated
    print

    print '* delete the last row'
    del m[2]
    print 'deleted:', m.deleted
    print

    print '* add a row'
    m.add_row((None, 'mosky', 'mosky@ubuntu-tw.org'))
    print 'inserted:', m.inserted

    print '* print the rows in the model again:'
    for i, row in enumerate(m):
        print '%d:' % i, row
    print
