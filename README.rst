The full version of this documentation is at `mosql.mosky.tw <http://mosql.mosky.tw>`_.

MoSQL --- More than SQL
=======================

MoSQL is a lightweight Python library which assists programmer to use SQL.

It has two major parts:

1. `An Easy-to-Use Model`_ for the result set.
2. `The SQL Builders`_ which build the SQL strings by the common data types in Python.

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

The `mosql.result.Model <http://mosql.mosky.tw/result.html#mosql.result.Model>`_ act as a proxy of the result set. After `configuring <http://mosql.mosky.tw/result.html#tutorial-of-model>`_, it provides a nice inferface to access the rows.

::

    >>> from my_models import Detail
    >>> for detail in Detail.find(person_id='mosky')):
    ...     print detail
    {'person_id': 'mosky', 'detail_id': [3, 4], 'val': ['address', '...'], 'key': 'address'}
    {'person_id': 'mosky', 'detail_id': [1, 6, 10], 'val': ['email', '...', '...'], 'key': 'email'}

For simplicity, the Model, which is a *dict-like* object, is rendered as a dict, and the `mosql.result.Column <http://mosql.mosky.tw/result.html#mosql.result.Column>`_, which is a *list-like* object, is rendered as a list.

As you see, some of the columns aren't rendered as lists, because they are the columns grouped. It is the feature `Model <http://mosql.mosky.tw/result.html#mosql.result.Model>`_ provides. It is more convenient than using SQL's ``group by``.

If you want to modify this model, just treat them as a dict or a list. The model will record your changes and let you save the changes at any time.

::

    >>> detail = Detail.find(person_id='mosky', key='email')
    >>> detail['val'][0] = 'I changed my email.'
    >>> # detail.val[0] = 'I changed my email.' # It also works in 0.1.1 .
    >>> detail.save()

`Start with MoSQL’s model <http://mosql.mosky.tw/result.html#tutorial-of-model>`_ describes more details about how to use the Model.

The SQL Builders
----------------

The above model is based on these SQL builders. For an example:

::

    >>> from mosql.common import select
    >>> select('person', {'age >': 18})
    'SELECT * FROM person WHERE age > 18'

It converts the common data types in Python into the SQL statements. 

You can find more exmaples in `mosql.common <http://mosql.mosky.tw/builders.html#module-mosql.common>`_. If the common builders aren't enough in your case, it is possible to customize the builder by `mosql.util <http://mosql.mosky.tw/builders.html#module-mosql.util>`_.

Installation
------------

It is easy to install MoSQL with pip:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git
