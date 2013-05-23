#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from mosql.result2 import Model

class PostgreSQL(Model):
    getconn = classmethod(lambda cls: psycopg2.connect(database='mosky'))
    putconn = classmethod(lambda cls, conn: None)

class Person(PostgreSQL):
    clauses = dict(table='person')
    arrange_by = ('person_id', )

class Detail(PostgreSQL):
    clauses = dict(table='detail')
    arrange_by = ('person_id', 'key')
    squashed = arrange_by
    ident_by = ('detail_id', )

if __name__ == '__main__':

    from pprint import pprint

    d = next(Detail.arrange(where={'person_id': 'mosky'}))

    print '# original'
    pprint(dict(d))
    print

    print '# setitem'
    d['val', 0] = 'modified@email.com'
    pprint(dict(d))
    print

    print '# append'
    d.append({'val': 'new@email.com'})
    pprint(dict(d))
    print

    print '# pop it'
    d.pop(0)
    pprint(dict(d))
    print

    print '# save it'
    d.save()
