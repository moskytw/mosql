#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It provides common standard SQL functions.'''

__all__ = [
    'avg', 'count', 'min', 'max', 'stddev', 'sum', 'variance'
]

from .util import raw, concat_by_comma, identifier

def _make_simple_function(name):

    def simple_function(*args):
        return raw('%s(%s)' % (
            name.upper(),
            concat_by_comma(identifier(x) for x in args)
        ))

    return simple_function

avg      = _make_simple_function('AVG')
count    = _make_simple_function('COUNT')
min      = _make_simple_function('MIN')
max      = _make_simple_function('MAX')
stddev   = _make_simple_function('STDDEV')
sum      = _make_simple_function('SUM')
variance = _make_simple_function('VARIANCE')
