#!/bin/bash

cd `git rev-parse --show-toplevel 2> /dev/null`
nosetests --with-doctest -Imysql -v mosql/ tests/
