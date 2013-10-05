#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common standard SQL functions.
'''

__all__ = [
    'avg', 'count', 'min', 'max', 'stddev', 'sum', 'variance'
]

from .util import Function

avg      = Function('AVG')
count    = Function('COUNT')
min      = Function('MIN')
max      = Function('MAX')
stddev   = Function('STDDEV')
sum      = Function('SUM')
variance = Function('VARIANCE')
