.PHONY: docs open prepare test test-all

docs:
	$(MAKE) -C docs html

open: docs
	open docs/_build/html/index.html

prepare:
	$(MAKE) -C docs pickle >/dev/null 2>&1

test: prepare
	python runtests.py

test-all: prepare
	tox
