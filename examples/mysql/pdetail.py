#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import MySQL
from mosql import build

class PersonDetail(MySQL):
    clauses = dict(table='detail', joins=build.join('person'))
    arrange_by = ('person_id', 'key')
    squashed = ('person_id', 'key', 'name')

if __name__ == '__main__':
    
    pdetail = PersonDetail.select(where=dict(person_id='mosky'))
    print pdetail
