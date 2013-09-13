#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .util import Query
from .statement import insert, select, update, delete, join

insert = Query(insert)
select = Query(select)
update = Query(update)
delete = Query(delete)

join       = Query(join)
left_join  = Query(join, {'type': 'left'})
right_join = Query(join, {'type': 'right'})
cross_join = Query(join, {'type': 'cross'})
