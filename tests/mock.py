#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mosql.result import Model

class Order(Model):
    arrange_by = ('order_id', )
    squashed = set(arrange_by)

col_names = ['order_id', 'product_id', 'price']

rows = [
    ('A001', 'A', 100, ),
    ('A001', 'B', 120, ),
    ('A001', 'C',  10, ),
    ('A002', 'D', 100, ),
    ('A002', 'E',  50, ),
]
