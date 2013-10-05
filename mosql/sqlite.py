#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the sqlite-specific stuff to :mod:`mosql.util`.

The usage:

::

    import mosql.sqlite

It will replace the functions in :mod:`mosql.util` with its functions.
'''


def format_param(s=''):
    return ':%s' % s if s else '?'

import mosql.util
mosql.util.format_param = format_param


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    #from timeit import timeit
    #from functools import partial

    #timeit = partial(timeit, number=100000)
    #bytes = ''.join(chr(i) for i in range(256))

    #def _escape(s):
    #    return s.replace("'", "''")

    #print timeit(lambda: _escape(bytes))
    ## -> 0.118767976761

    #print timeit(lambda: escape(bytes))
    ## -> 7.97847890854

    #print timeit(lambda: fast_escape(bytes))
    ## -> 0.155963897705
