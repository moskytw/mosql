#!/usr/bin/env python
# -*- coding: utf-8 -*-

def delimit_identifier(s):
    '''It delimits the identifier.'''
    return str(s)

import mosql.util

def patch():
    '''Applies the YQL-specific functions again.'''
    mosql.util.delimit_identifier = delimit_identifier

patch() # patch it when load this module
