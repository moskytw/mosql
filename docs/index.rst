.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

MoSQL is a lightweight Python library which assists programmer to use SQL.

It has two major parts:

The first part is SQL builders which help you to build SQL with common Python data types:

::

    >>> from mosql.common import select
    >>> select('person', {'age >': 18})
    'SELECT * FROM person WHERE age > 18'

It converts the Python data types to SQL statements. You can find more exmaples in :py:mod:`mosql.common`.

The second part is a hyper abstarct of the result set:

::

    >>> from my_models import Detail
    >>> for detail in Detail.find(person_id='mosky')):
    ...     print detail
    {'person_id': 'mosky', 'detail_id': [3, 4], 'val': ['address', '...'], 'key': 'address'}
    {'person_id': 'mosky', 'detail_id': [5, 6, 7], 'val': ['email', '...', '...'], 'key': 'email'}

The :py:class:`mosql.result.Model` rendered in a dict is a dict-like object. And the lists in the :py:class:`~mosql.result.Model` are :py:class:`mosql.result.Column`. The :py:class:`~mosql.result.Column` is a proxy. It will redirect your changes on it to :py:class:`~mosql.result.Model`.

Installation
------------

It is easy to install MoSQL with `pip`:

::

    $ sudo pip install mosql

Or clone the source code from `Github`:

::

    $ git clone git://github.com/moskytw/mosql.git

The documentions
================

.. toctree::
    :maxdepth: 2

    result.rst
    builders.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

