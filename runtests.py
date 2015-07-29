#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import nose

from nose_exclude import NoseExclude
from sphinxnose import SphinxDoctest

exclude = NoseExclude()
sphinxtests = SphinxDoctest()


if __name__ == '__main__':
    argv = [__file__, '--with-sphinx']
    ok = nose.run(argv=argv, plugins=[exclude, sphinxtests])
    if not ok:
        sys.exit(1)
