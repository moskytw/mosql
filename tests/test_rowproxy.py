#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mosql.result import Model

class Order(Model):
    arrange_by = ('order_id', )
    squashed = set(arrange_by)

rows = [
    ('A001', 'A', 100, ),
    ('A001', 'B', 120, ),
    ('A001', 'C',  10, ),
    ('A002', 'D', 100, ),
    ('A002', 'E',  50, ),
]

print '# Order'
for order in Order.arrange_rows(['order_id', 'product_id', 'price'], rows):
    print order
print

print '# Rows in Order'
for row in order.rows():
    print row
print

print '# Modification'
row.price = 99
print 'This row  :', row
print 'This order:', order
