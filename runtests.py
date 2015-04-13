#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import nose

from nose_exclude import NoseExclude
from sphinxnose import SphinxDoctest

exclude = NoseExclude()
sphinxtests = SphinxDoctest()


if __name__ == '__main__':
    ok = nose.run(
        argv=[__file__, '--with-sphinx', '--exclude-dir=oldtests'],
        plugins=[exclude, sphinxtests],
    )
    if not ok:
        sys.exit(1)
