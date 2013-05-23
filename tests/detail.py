#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import PostgreSQL

class Detail(PostgreSQL):
    clauses = dict(table='detail')
    arrange_by = ('person_id', 'key')
    squashed = arrange_by
    ident_by = ('detail_id', )

if __name__ == '__main__':
    pass
