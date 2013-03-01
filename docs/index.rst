.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

MoSQL is a lightweight Python library assists programmer to use SQL.

It has two major parts:

The first part is SQL builders helps you to build SQL with common Python data type:

::

    >>> from mosql.common import select
    >>> select('person', {'age >': 18})
    'SELECT * FROM person WHERE age > 18'

It converts the Python types to SQL statements. You can find more exmaples in :py:mod:`mosql.common`.

The second part is a hyper abstarct of the result set:

::

    >>> from my_models import Detail
    >>> for detail in Detail.find(person_id='mosky')):
    ...     print detail
    {'person_id': 'mosky', 'detail_id': [3, 4], 'val': ['address', '...'], 'key': 'address'}
    {'person_id': 'mosky', 'detail_id': [5, 6, 7], 'val': ['email', '...', '...'], 'key': 'email'}

The returned objects are not just dicts or lists. They are proxies record your operations on it, and allow you to save them back to database.

It is acceptable to feed the raw result set to a :py:class:`~mosql.result.Model` by :py:meth:`~mosql.result.Model.group`. It's up to you.

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

    api.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

