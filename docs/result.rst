Handling of Result Set 
======================

.. _tutorial-of-model:

Start with MoSQL's model
------------------------

The result set
^^^^^^^^^^^^^^

Let us start from the basic library conformed the `Python DB API 2.0 <http://www.python.org/dev/peps/pep-0249/>`_. Here are some snippets of querying data from PostgreSQL_ with Psycopg2_:

::

    from pprint import pprint
    import psycopg2

    conn = psycopg2.connect(database='mosky')
    cur = conn.cursor()

    cur.execute("select detail_id, person_id, key, val from detail where person_id = 'mosky'")
    pprint(cur.fetchall())

And here is the result:

::

    [(4, 'mosky', 'address', 'It is my second address.'),
     (3, 'mosky', 'address', 'It is my first address.'),
     (10, 'mosky', 'email', 'It is my third email.'),
     (2, 'mosky', 'email', 'It is my second email.'),
     (1, 'mosky', 'email', 'It is my first email.')]

We may change some value after checking the reuslt:

::

    cur.execute("update detail set val='changed' where detail_id=10")

    conn.commit()

As you saw, we need to compose the SQLs to select or update, and arrange the result set from databse. All of them are annoying works.

Let :py:class:`mosql.result.Model` do those things for you!

.. _PostgreSQL: http://postgresql.org
.. _Psycopg2: http://initd.org/psycopg

Group the result set
^^^^^^^^^^^^^^^^^^^^

You have to inherit :py:class:`mosql.result.Model` to customize your model for different result sets.

For an example, you will need a model like this for the above data:

::

    from model.result import Model

    class Detail(Model):
        columns_names = ('detail_id', 'person_id', 'key', 'val')
        group_by      = ('person_id', 'key')

And use it to sort the result set:

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

It is a dict-like object, so you can update the value via setting item.

::

    detail['val'][0] = 'changed'
    print detail

::

    {'person_id': 'mosky', 'detail_id': [10, 2, 1], 'val': ['changed', 'It is my second email.', 'It is my first email.'], 'key': 'email'}

.. versionadded:: 0.1.1
    ``detail.val[0] = 'changed'`` is also accepted.

Drop out the SQLs
^^^^^^^^^^^^^^^^^

`Pool` defines the how `Model` gets and puts the connection with database. Here is a simple implement of a `Pool`:

::

    class DummyPool(object):

        def getconn(self):
            if not hasattr(self, 'conn')
                self.conn = psycopg2.connect(database='dbname')
            return self.conn

        def putconn(self, conn):
            pass

And let `Model` use this `Pool` and set the name of table:

::

    class Detail(Model):
        ...
        table_name = 'detail'
        pool       = DummyPool()
        ...

.. note::
    The above APIs may be changed in further version.

.. note::
    If you are using `Psycopg <http://initd.org/psycopg/>`_, you can use its `Connections Pool <http://initd.org/psycopg/docs/pool.html>`_ directly.

Then, you can use the Model's :py:meth:`~mosql.result.Model.find` instead of the select.

::

    for detail in Detail.find(person_id='mosky'):
        print detail

::

    {'person_id': 'mosky', 'detail_id': [4, 3], 'val': ['It is my second address.', 'It is my first address.'], 'key': 'address'},
    {'person_id': 'mosky', 'detail_id': [10, 2, 1], 'val': ['It is my third email.', 'It is my second email.', 'It is my first email.'], 'key': 'email'}

The `Model` will cache the changes, so you need to use Model's :py:meth:`~mosql.result.Model.save` to save changes back.

::

    Detail.dump_sql = True # for debug
    detail['val'][0] = 'changed'
    detal.save()

::

    ["UPDATE detail SET val = 'changed' WHERE person_id = 'mosky' AND detail_id = 1 AND val = 'It is my first email.' AND key = 'email'"]

The SQL seems stupid. You can teach model how to identify a row.

::

    class Detail(Model):
        ...
        identify_by = ('detail_id',)
        ...

The SQL will be more accurate:

::

    ["UPDATE detail SET val = 'changed' WHERE detail_id = 1"]

.. warning::
    In 0.1.0, you must specify the `identify_by` -- otherwise it will generate a update SQL without any condition.

Although this section named '*Drop out* the SQLs', but MoSQL doesn't aim to create a world without SQL. SQL is the key of application's performance, and MoSQL just try to reduce the complexity of building SQL.

.. seealso::
    `mosql/tests <https://github.com/moskytw/mosql/tree/master/tests>`_ --- there are some real examples.

.. seealso::
    :ref:`builders` --- it describes how those SQLs was built.

The API --- :py:mod:`mosql.result`
----------------------------------

.. automodule:: mosql.result
    :members:
