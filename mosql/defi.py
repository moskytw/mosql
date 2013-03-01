#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A hyper None, because None represents null in SQL.
Empty = ___ = type('Empty', (object, ), {
    '__nonzero__': lambda self: False,
    '__str__'    : lambda self: '___',
    '__repr__'   : lambda self: 'Empty',
})()

default = type('default', (object, ), {
    '__str__'   : lambda self: 'DEFAULT',
    '__repr__'   : lambda self: 'default',
})()

