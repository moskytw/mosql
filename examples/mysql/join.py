#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mosql import build

from base import MySQL
from detail import Detail
from person import Person

class PersonDetail(Detail):
    squashed   = set(['person_id', 'name'])
    clauses    = dict(
        order_by = Detail.arrange_by,
        joins    = build.join('person')
    )

if __name__ == '__main__':

    # if you want to see the SQLs it generates
    #PersonDetail.dump_sql = True

    print "# Show the Mosky's Detail"
    print
    for pdetail in PersonDetail.find(person_id='mosky'):
        print pdetail
    print
    
