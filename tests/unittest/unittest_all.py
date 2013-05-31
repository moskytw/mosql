#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

def load_tests(loader, tests, ignore):

    from os.path import dirname, join, abspath
    itsdir = dirname(__file__)

    import sys
    sys.path.insert(0, abspath(join(itsdir, '..')))
    sys.path.insert(0, abspath(itsdir))

    import doctest

    # ValueError: (<module 'mosql.defi' from '/home/mosky/sql-helper/mosql/defi.pyc'>, 'has no tests')
    #import mosql.defi
    #tests.addTests(doctest.DocTestSuite(mosql.defi))

    import mosql.util
    tests.addTests(doctest.DocTestSuite(mosql.util))

    import mosql.build
    tests.addTests(doctest.DocTestSuite(mosql.build))

    #import mosql.ext
    #tests.addTests(doctest.DocTestSuite(mosql.ext))

    import mosql.result
    tests.addTests(doctest.DocTestSuite(mosql.result))

    import unittest_model
    tests.addTest(loader.loadTestsFromModule(unittest_model))

    return tests

if __name__ == '__main__':
    unittest.main(verbosity=2)
