#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import PostgreSQL
from mosql import build

class PersonDetail(PostgreSQL):
    table      = 'detail'
    clauses    = dict(joins=build.join('person'))
    arrange_by = set(['person_id', 'key'])
    squash_by  = ('person_id', 'key', 'name')

if __name__ == '__main__':
    
    pdetail = PersonDetail.select(dict(person_id='mosky'))
    print pdetail
