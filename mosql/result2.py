#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import groupby
from collections import Mapping

from . import common as build
from . import util

def get_col_names(cur):
    return [row_desc[0] for row_desc in cur.description]

def hash_dict(d):
    return hash(frozenset(d.items()))

class Model(Mapping):

    # --- connection-related ---

    @classmethod
    def getconn(cls):
        raise NotImplementedError('This method should return a connection.')

    @classmethod
    def putconn(cls, conn):
        raise NotImplementedError('This method should accept a connection.')

    dump_sql = False
    dry_run = False

    @classmethod
    def perform(cls, sql_or_sqls):

        conn = cls.getconn()
        cur = conn.cursor()

        if isinstance(sql_or_sqls, basestring):
            sqls = [sql_or_sqls]
        else:
            sqls = sql_or_sqls

        if cls.dump_sql:
            print '--- SQL DUMP ---'
            for sql in sqls:
                print sql
            print '--- END ---'

        try:
            cur.execute('; '.join(sqls))
        except:
            conn.rollback()
            raise
        else:
            if cls.dry_run:
                conn.rollback()
            else:
                conn.commit()

        cls.putconn(conn)

        return cur

    # --- translate result set to a model or models ---

    col_names = tuple()

    @classmethod
    def load_rows(cls, col_names, rows):

        m = cls()
        m.col_names = col_names

        m.cols = dict((name, [
            row[i] for row in rows
        ]) for i, name in enumerate(m.col_names))

        return m

    @classmethod
    def load_cur(cls, cur):
        return cls.load_rows(get_col_names(cur), cur.fetchall())

    arrange_by = tuple()

    @classmethod
    def arrange_rows(cls, col_names, rows):

        name_index_map = dict((name, i) for i, name  in enumerate(col_names))
        key_indexes = tuple(name_index_map[name] for name in cls.arrange_by)
        key_func = lambda row: tuple(row[i] for i in key_indexes)

        for _, rows in groupby(rows, key_func):
            yield cls.load_rows(col_names, list(rows))

    @classmethod
    def arrange_cur(cls, cur):
        return cls.arrange_rows(get_col_names(cur), cur.fetchall())

    # --- shortcuts of Python data structure -> SQL -> result set -> model ---

    clauses = {}

    @classmethod
    def load(cls, *args, **kargs):
        mixed_kargs = cls.clauses.copy()
        mixed_kargs.update(kargs)
        return cls.load_cur(cls.perform(build.select(*args, **mixed_kargs)))

    @classmethod
    def arrange(cls, *args, **kargs):
        mixed_kargs = cls.clauses.copy()
        mixed_kargs.update(kargs)
        return cls.arrange_cur(cls.perform(build.select(*args, **mixed_kargs)))

    # --- read this model ---

    squashed = set()

    def col(self, col_name):
        return self.cols[col_name]

    def __iter__(self):
        return (name for name in self.col_names)

    def __len__(self):
        return len(self.col_names)

    def row(self, row_idx):
        return [self.cols[col_name][row_idx] for col_name in self.col_names]

    def __getitem__(self, col_row):

        if isinstance(col_row, basestring):
            col_name = col_row
            if col_name in self.squashed:
                return self.cols[col_name][0]
            else:
                return self.cols[col_name]
        else:
            col_name, row_idx = col_row
            return self.cols[col_name][row_idx]

    # --- modifiy this model --- 

    ident_by = None

    def __init__(self):
        self.changes = []
        self.cols = {}

    def ident(self, row_idx):

        ident_by = self.ident_by
        if ident_by is None:
            ident_by = self.col_names

        ident = {}
        for col_name in ident_by:
            val = self[col_name][row_idx]
            if val is util.default:
                raise ValueError("value of column %r is not decided yet." % col_name)
            ident[col_name] = val

        return ident

    def __setitem__(self, col_row, val):

        if isinstance(col_row, basestring):
            col_name = col_row
            for i in range(len(self.cols[col_name])):
                self[col_name, i] = val
        else:
            col_name, row_idx = col_row
            self.changes.append((self.ident(row_idx), {col_name: val}))
            self.cols[col_name][row_idx] = val

    def pop(self, row_idx=-1):

        self.changes.append((self.ident(row_idx), None))

        for col_name in self.col_names:
            self.cols[col_name].pop(row_idx)

    def assume(self, row_map):

        row_map = row_map.copy()

        for col_name in row_map:

            if col_name in row_map:
                val = row_map[col_name]
            elif col_name in self.squashed:
                val = row_map[col_name] = self.cols[col_name][0]
            else:
                val = row_map[col_name] = util.default

            self.cols[col_name] = val

        return row_map

    def append(self, row_map):
        self.changes.append((None, self.assume(row_map)))

    def save(self):

        sqls = []

        if not self.changes:
            return

        for i, (cond, val) in enumerate(self.changes):

            if cond is None:
                sqls.append(build.insert(pairs_or_columns=val, **self.clauses))
            elif val is None:
                sqls.append(build.delete(where=cond, **self.clauses))
            else:

                # find other update changes which cond is target_cond
                target_cond = cond
                cond_hash = hash_dict(target_cond)

                merged_val = val.copy()
                merged_idxs = []

                for j in range(i+1, len(self.changes)):

                    cond, val = self.changes[j]

                    # skip not update changes
                    if cond is None or val is None:
                        continue

                    if hash_dict(cond) == cond_hash:
                        merged_val.update(val)
                        merged_idxs.append(j)

                for j in reversed(merged_idxs):
                    self.changes.pop(j)

                sqls.append(build.update(where=target_cond, set=merged_val, **self.clauses))

        self.changes = []

        return self.perform(sqls)
