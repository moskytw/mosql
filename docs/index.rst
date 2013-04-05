.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

MoSQL is a lightweight Python library which assists programmer to use SQL.

It has two major parts:

1. :ref:`an-easy-to-use-model` for the result set.
2. :ref:`the-sql-builders` which build the SQL strings by the common data types in Python.

.. _an-easy-to-use-model:

An Easy-to-Use Model
--------------------

I show you an example with this result set:

::

    db=> select * from detail where person_id='mosky';
     detail_id | person_id |   key   |   val            
    -----------+-----------+---------+---------
             4 | mosky     | address | address
             3 | mosky     | address | ...
            10 | mosky     | email   | email
             6 | mosky     | email   | ...
             1 | mosky     | email   | ...
    (5 rows)

The :py:class:`mosql.result.Model` act as a proxy of the result set. After `configuring </result.html#tutorial-of-model>`_, it provides a nice inferface to access the rows.

::

    >>> from my_models import Detail
    >>> for detail in Detail.find(person_id='mosky')):
    ...     print detail
    {'person_id': 'mosky', 'detail_id': [3, 4], 'val': ['address', '...'], 'key': 'address'}
    {'person_id': 'mosky', 'detail_id': [1, 6, 10], 'val': ['email', '...', '...'], 'key': 'email'}

For simplicity, the Model, which is a *dict-like* object, is rendered as a dict, and the :py:class:`mosql.result.Column`, which is a *list-like* object, is rendered as a list.

As you see, some of the columns aren't rendered as lists, because they are the columns grouped. It is the feature :py:class:`~mosql.result.Model` provides. It is more convenient than using SQL's ``group by``.

If you want to modify this model, just treat them as a dict or a list. The model will record your changes and let you save the changes at any time.

::

    >>> detail = Detail.find(person_id='mosky', key='email')
    >>> detail['val'][0] = 'I changed my email.'
    >>> # detail.val[0] = 'I changed my email.' # It also works in 0.1.1 .
    >>> detail.save()

:ref:`tutorial-of-model` describes more details about how to use the Model.

.. _the-sql-builders:

The SQL Builders
----------------

The above model is based on these SQL builders. For an example:

::

    >>> from mosql.common import select
    >>> select('person', {'age >': 18})
    'SELECT * FROM person WHERE age > 18'

It converts the common data types in Python into the SQL statements. 

You can find more exmaples in :py:mod:`mosql.common`. If the common builders aren't enough in your case, it is possible to customize the builder by :py:mod:`mosql.util`.


Installation
------------

It is easy to install MoSQL with pip:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git

The Documentions
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
