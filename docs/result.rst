Handling of Result Set 
======================

.. _tutorial-of-model:

Start with MoSQL's Model
------------------------

The :py:class:`mosql.result.Model` works well without any other library, but it is better to cooperate with a library which conforms the `Python DB API 2.0`_, such as `Psycopg <http://initd.org/psycopg/>`_ (for PostgreSQL) or `MySQLdb <http://sourceforge.net/projects/mysql-python/>`_ (for MySQL).

This tutorial has three sections:

1. `The Pure SQL`_ introduces how to use a library conformed `Python DB API 2.0` and the advantages of using :py:class:`~mosql.result.Model`.
2. `Group the Result Set`_ explains the basic configuration of using :py:class:`~mosql.result.Model`.
3. `Drop the SQLs out`_ shows how to work without the SQLs. 

The Pure SQL
^^^^^^^^^^^^

Here are some code snippets of using the basic library conformed the `Python DB API 2.0`_.

::

    import psycopg2

    conn = psycopg2.connect(database='mosky')
    cur = conn.cursor()

    cur.execute("select detail_id, person_id, key, val from detail where person_id = 'mosky'")

    from pprint import pprint
    pprint(cur.fetchall())

::

    [(4, 'mosky', 'address', 'It is my second address.'),
     (3, 'mosky', 'address', 'It is my first address.'),
     (10, 'mosky', 'email', 'It is my third email.'),
     (2, 'mosky', 'email', 'It is my second email.'),
     (1, 'mosky', 'email', 'It is my first email.')]

The above are the code and result of normal SQL select.

::

    cur.execute("update detail set val='changed' where detail_id=10")

    conn.commit()

And we will use the above pattern to change the data in a database.

As you see, there are two main problems:

1. The result set always needs to arrange to the form which is easy to use (ex. a dict).
2. The hand-made SQLs are alien to Python. It is hard to build a SQL without any library.

Although here are two problems, it has a *big* advantage --- the performance is the **best** in this way.

The :py:class:`~mosql.result.Model` is designed to solve the problems and keep the advantage as complete as possible.

.. _`Python DB API 2.0`: http://www.python.org/dev/peps/pep-0249/

Group the Result Set
^^^^^^^^^^^^^^^^^^^^

The :py:class:`~mosql.result.Model` works well with traditional way. It provides a useful method: :py:meth:`~mosql.result.Model.group`. It can group the result set from a normal cursor.

Before we use it, we need to customize the Model for fitting our result set:

::

    from mosql.result import Model

    class Detail(Model):
        column_names = ('detail_id', 'person_id', 'key', 'val')
        group_by     = ('person_id', 'key')

.. warning::
    In v0.1.0, you must list all of the column names. It is fixed in v0.1.1.

Then, use the `group` method to group our result set:

::

    cur.execute("select detail_id, person_id, key, val from detail where person_id = 'mosky'")

    for detail in Detail.group(cur):
        for col_name in detail:
            print '%-9s: %s' % (col_name, detail[col_name])
        print

::

    detail_id: [4, 3]
    person_id: mosky
    key      : address
    val      : ['It is my second address.', 'It is my first address.']

    detail_id: [10, 2, 1]
    person_id: mosky
    key      : email
    val      : ['It is my third email.', 'It is my second email.', 'It is my first email.']

It is better than original result set, right? And it is transparent for the SQL experts.

And it is just a dict-like object, so you can update the value via setting a new value to them.

::

    detail['val'][0] = 'changed'
    print detail

::

    {'person_id': 'mosky', 'detail_id': [10, 2, 1], 'val': ['changed', 'It is my second email.', 'It is my first email.'], 'key': 'email'}

.. versionadded:: 0.1.1
    ``detail.val[0] = 'changed'`` is also accepted.

Drop the SQLs out
^^^^^^^^^^^^^^^^^

Of course, the :py:class:`~mosql.result.Model` is not just a grouper. It also provides a nice interface of executing SQLs.

For letting Model talk with database, you must define an interface which gets or puts the connection. The :py:class:`mosql.result.Pool` is a such interface. The built-in Pool is an abstract class. You need to define you own Pool. Here is a simple example:

::

    class DummyPool(object):

        def getconn(self):
            if not hasattr(self, 'conn'):
                self.conn = psycopg2.connect(database='dbname')
            return self.conn

        def putconn(self, conn):
            pass

.. note::
    If you are using `Psycopg <http://initd.org/psycopg/>`_, the Pool we mentioned is equal to its `Connections Pool <http://initd.org/psycopg/docs/pool.html>`_.

.. note::
    If you are using `official MySQL connector for Python <https://pypi.python.org/pypi/mysql-connector-python>`_, you may need to set ``buffered`` argument to True in the ``connect``.

Then, for applying the changes, the Model have to know the name of table.

After prepared the above materials, put them into the Model:

::

    class Detail(Model):
        ...
        table_name = 'detail'
        pool       = DummyPool()
        ...

Then, you can use the Model's :py:meth:`~mosql.result.Model.find` (or :py:meth:`~mosql.result.Model.seek`) instead of the select.

::

    for detail in Detail.find(person_id='mosky'):
        print detail

::

    {'person_id': 'mosky', 'detail_id': [4, 3], 'val': ['It is my second address.', 'It is my first address.'], 'key': 'address'},
    {'person_id': 'mosky', 'detail_id': [10, 2, 1], 'val': ['It is my third email.', 'It is my second email.', 'It is my first email.'], 'key': 'email'}

Let us try to change something and save it to databsse.

::

    Detail.dump_sql = True # for showing the SQL it built
    detail['val'][0] = 'changed'
    detal.save()

The Model will cache the changes in itself, so you need to use Model's :py:meth:`~mosql.result.Model.save` to save the changes back.

::

    ["UPDATE detail SET val = 'changed' WHERE person_id = 'mosky' AND detail_id = 1 AND val = 'It is my first email.' AND key = 'email'"]

Uh, I think some SQL experts can't accept this SQL, because it is too imprecise. We have solution for it. You can teach the Model how to identify a row by adding a tuple:

::

    class Detail(Model):
        ...
        identify_by = ('detail_id',)
        ...

The SQL it generated will be more accurate:

::

    ["UPDATE detail SET val = 'changed' WHERE detail_id = 1"]

.. warning::
    In 0.1.0, you must specify the `identify_by` -- otherwise it will generate a update SQL without any condition. That's terrible. It is fixed in v0.1.1.

That's all. You may want to know more methods the Model provides: :ref:`model-api`.

.. seealso::
    `mosql/examples <https://github.com/moskytw/mosql/tree/master/examples>`_ --- there are some real examples.

.. seealso::
    :ref:`builders` --- it describes how :py:class:`~mosql.result.Model` to build those SQL from Python's data types.

.. _model-api:

The API --- :py:mod:`mosql.result`
----------------------------------

.. automodule:: mosql.result
    :members:

The Compatible JSON encoder and decoder --- :py:mod:`mosql.json`
----------------------------------------------------------------

.. automodule:: mosql.json
    :members:
