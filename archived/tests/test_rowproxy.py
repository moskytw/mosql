#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import Order, col_names, rows

print '# Order'
for order in Order.arrange_rows(col_names, rows):
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
