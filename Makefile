.PHONY: docs open prepare-test release test test-all

all:
	python setup.py sdist bdist_wheel

docs:
	$(MAKE) -C docs html

open: docs
	open docs/_build/html/index.html

prepare-test:
	$(MAKE) -C docs pickle >/dev/null 2>&1

release: all
	upload

test: prepare-test
	python runtests.py

test-all: prepare-test
	tox
