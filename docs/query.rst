The Common Queries --- :mod:`mosql.query`
=========================================

This module provides the common :class:`~mosql.util.Query` instances for you.

The basic queries are here:

- :func:`~mosql.query.select`
- :func:`~mosql.query.insert`
- :func:`~mosql.query.update`
- :func:`~mosql.query.delete`

It also provides various join queries, use them with the above queries:

- :func:`~mosql.query.join`
- :func:`~mosql.query.left_join`
- :func:`~mosql.query.right_join`
- :func:`~mosql.query.cross_join`

The non-standard queries are also available:

- :func:`~mosql.query.replace`

If you want to build you own, there are all basic bricks you need -
:doc:`/util`.

.. note::

    If you are using non-standard SQL, such as MySQL, check :doc:`patches`.

.. versionadded:: v0.6

.. py:module:: mosql.query

.. testsetup::

    from mosql.query import select, insert, update, delete, replace
    from mosql.query import join, left_join, right_join, cross_join
    from mosql.util import param, ___, raw

.. py:function:: select(table=None, where=None, **clause_args)

    It generates the SQL statement, ``SELECT ...`` .


    Use `dict` or `pairs` to represent a where condition:

    >>> print(select('person', {'person_id': 'mosky'}))
    SELECT * FROM "person" WHERE "person_id" = 'mosky'

    >>> print(select('person', (('person_id', 'mosky'), )))
    SELECT * FROM "person" WHERE "person_id" = 'mosky'

    >>> print(select('person', {'name like': 'Mosky%'}, limit=3, offset=1))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1


    The operator will be decided automatically:

    >>> print(select('person', {'person_id': ('andy', 'bob')}))
    SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')

    >>> print(select('person', {'name': None}))
    SELECT * FROM "person" WHERE "name" IS NULL

    And also allow to customize::

        >>> print(select('person', {'name like': 'Mosky%', 'age >': 20}))
        SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'

        >>> print(select('person', {('name', 'like'): 'Mosky%', ('age', '>'): 20}))
        SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'

        >>> print(select('person', {"person_id = '' OR true; --": 'mosky'}))
        Traceback (most recent call last):
            ...
        OperatorError: this operator is not allowed: "= '' OR TRUE; --"

    .. seealso::
        The operators allowed --- :attr:`mosql.util.allowed_operators`.

    The ambiguous cases that :class:`~mosql.util.Query` works around for you:

    >>> print(select('person', {'person_id': ()}))
    SELECT * FROM "person" WHERE FALSE

    >>> print(select('person', where=None))
    SELECT * FROM "person"

    >>> print(select('person', where={}))
    SELECT * FROM "person"

    .. seealso::
        How it builds where clause --- :func:`mosql.util.build_where`


    The `columns` is an alias of standard clause argument, `select`. Any simple
    `iterable` represents the list in SQL. It also understands the ``.`` (dot)
    and even ``AS`` in your string.

    >>> print(select('person', select=('person.person_id', 'person.name')))
    SELECT "person"."person_id", "person"."name" FROM "person"

    >>> print(select('person', columns=('person.person_id', 'person.name')))
    SELECT "person"."person_id", "person"."name" FROM "person"

    >>> print(select('person', columns=('person.person_id as id', 'person.name')))
    SELECT "person"."person_id" AS "id", "person"."name" FROM "person"

    .. seealso::
        How it handles identifier including ``AS`` --- :func:`mosql.util.identifier_as`


    Specify `group_by`, `having`, `order_by`, `limit`, and `offset` in keyword
    arguments:

    >>> print(select('person', {'name like': 'Mosky%'}, order_by=('age', )))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"

    >>> print(select('person', {'name like': 'Mosky%'}, order_by=('age desc', )))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC

    >>> print(select('person', {'name like': 'Mosky%'}, order_by=('age ; DROP person; --', )))  # doctest: +SKIP
    Traceback (most recent call last):
        ...
    DirectionError: this direction is not allowed: '; DROP PERSON; --'

    .. seealso::
        The directions allowed --- :attr:`mosql.util.allowed_directions`.


    The prepare statement is also available with :class:`mosql.util.param`::

        >>> print(select('table', {'custom_param': param('my_param'), 'auto_param': param, 'using_alias': ___}))
        SELECT * FROM "table" WHERE "auto_param" = %(auto_param)s AND "using_alias" = %(using_alias)s AND "custom_param" = %(my_param)s


    If you want to use functions, wrap it with :class:`mosql.util.raw`:

    >>> print(select('person', columns=raw('count(*)'), group_by=('age', )))
    SELECT count(*) FROM "person" GROUP BY "age"

    .. warning::
        It's your responsibility to ensure the security when you use
        :class:`raw` string.


    The PostgreSQL-specific ``FOR``, ``OF`` and ``NOWAIT`` are also supported:

    >>> print(select('person', {'person_id': 1}, for_='update', of=('person', ), nowait=True))
    SELECT * FROM "person" WHERE "person_id" = 1 FOR UPDATE OF "person" NOWAIT

    .. seealso::
        Check `PostgreSQL SELECT - The locking Clause
        <http://www.postgresql.org/docs/9.3/static/sql-select.html#SQL-FOR-UPDATE-SHARE>`_
        for more detail.


    The MySQL-specific ``FOR UPDATE`` and ``LOCK IN SHARE MODE`` are also available:

    >>> print(select('person', {'person_id': 1}, for_update=True))
    SELECT * FROM "person" WHERE "person_id" = 1 FOR UPDATE

    >>> print(select('person', {'person_id': 1}, lock_in_share_mode=True))
    SELECT * FROM "person" WHERE "person_id" = 1 LOCK IN SHARE MODE

    .. seealso::
        Check `MySQL Locking Reads
        <http://dev.mysql.com/doc/refman/5.7/en/innodb-locking-reads.html>`_ for
        more detail.


    Print it for the full usage:

    ::

        >>> print(select)
        select(table=None, where=None, *, select=None, from=None, joins=None, where=None, group_by=None, having=None, order_by=None, limit=None, offset=None, for=None, of=None, nowait=None, for_update=None, lock_in_share_mode=None)


    The last tip, echo the SQL to debug:

    ::

        >>> select.enable_echo()
        >>> sql = select()
        SELECT *
        >>> print sql
        SELECT *


    .. versionchanged:: 0.9
        Added ``FOR UPDATE``, ``LOCK IN SHARE MODE``, ``FOR``, ``OF``, and
        ``NOWAIT``.

.. py:function:: insert(table=None, set=None, **clause_args)

    It generates the SQL statement, ``INSERT INTO ...``.

    The following usages generate the same SQL statement:

    >>> print(insert('person', {'person_id': 'mosky', 'name': 'Mosky Liu'}))  # doctest: +SKIP
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    >>> print(insert('person', (('person_id', 'mosky'), ('name', 'Mosky Liu'))))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    >>> print(insert('person', columns=('person_id', 'name'), values=('mosky', 'Mosky Liu')))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    Sometimes we don't need the `columns`:

    >>> print(insert('person', values=('mosky', 'Mosky Liu')))
    INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')

    The `values` allows values-list:

    >>> print(insert('person', values=[('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')]))
    INSERT INTO "person" VALUES ('mosky', 'Mosky Liu'), ('yiyu', 'Yi-Yu Liu')

    All of the :func:`insert`, :func:`update` and :func:`delete` support ``returning``::

        >>> print(insert('person', {'person_id': 'mosky', 'name': 'Mosky Liu'}, returning=raw('*')))
        INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu') RETURNING *

    The MySQL-specific ``ON DUPLICATE KEY UPDATE`` is also supported:

    >>> print(insert('person', values=('mosky', 'Mosky Liu'), on_duplicate_key_update={'name': 'Mosky Liu'}))
    INSERT INTO "person" VALUES ('mosky', 'Mosky Liu') ON DUPLICATE KEY UPDATE "name"='Mosky Liu'

    Print it for the full usage::

        >>> print(insert)
        insert(table=None, set=None, *, insert_into=None, columns=None, values=None, returning=None, on_duplicate_key_update=None)

    .. versionchanged:: 0.10
        Let `values` supports values-list.

.. py:function:: replace(table=None, set=None, **clause_args)

    It generates the SQL statement, ``REPLACE INTO...``::

        >>> print(replace('person', {'person_id': 'mosky', 'name': 'Mosky Liu'}))
        REPLACE INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    It is almost same as :func:`insert`.

    Print it for the full usage::

        >>> print(replace)
        replace(table=None, set=None, *, replace_into=None, columns=None, values=None)

.. py:function:: update(table=None, where=None, set=None, **clause_args)

    It generates the SQL statement, ``UPDATE ...`` .

    The following usages generate the same SQL statement.

    >>> print(update('person', {'person_id': 'mosky'}, {'name': 'Mosky Liu'}))
    UPDATE "person" SET "name"='Mosky Liu' WHERE "person_id" = 'mosky'

    >>> print(update('person', (('person_id', 'mosky'), ), (('name', 'Mosky Liu'),) ))
    UPDATE "person" SET "name"='Mosky Liu' WHERE "person_id" = 'mosky'

    Print it for the full usage::

        >>> print(update)
        update(table=None, where=None, set=None, *, update=None, set=None, where=None, returning=None)

    .. seealso::
        How it builds the set clause --- :func:`mosql.util.build_set`

.. py:function:: delete(table=None, where=None, **clause_args)

    It generates the SQL statement, ``DELETE FROM ...`` .

    The following usages generate the same SQL statement.

    >>> print(delete('person', {'person_id': 'mosky'}))
    DELETE FROM "person" WHERE "person_id" = 'mosky'

    >>> print(delete('person', (('person_id', 'mosky'), )))
    DELETE FROM "person" WHERE "person_id" = 'mosky'

    Print it for the full usage::

        >>> print(delete)
        delete(table=None, where=None, *, delete_from=None, where=None, returning=None)

.. py:function:: join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``... JOIN ...`` .

    If you don't give `type`, nor `on` or `using`, the `type` will be
    ``NATURAL``; otherwise `type` will be ``INNER``.

    >>> print(select('person', joins=join('detail')))
    SELECT * FROM "person" NATURAL JOIN "detail"

    >>> print(select('person', joins=join('detail', {'person.person_id': 'detail.person_id'})))
    SELECT * FROM "person" INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"

    >>> print(select('person', joins=join('detail', using=('person_id', ))))
    SELECT * FROM "person" INNER JOIN "detail" USING ("person_id")

    >>> print(select('person', joins=join('detail', using=('person_id', ), type='left')))
    SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")

    >>> print(select('person', joins=join('detail', type='cross')))
    SELECT * FROM "person" CROSS JOIN "detail"

    Print it for the full usage::

        >>> print(join)
        join(table=None, on=None, *, type=None, join=None, on=None, using=None)

    .. seealso::
        How it builds the on clause --- :func:`mosql.util.build_on`

.. py:function:: left_join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``LEFT JOIN ...`` .

    >>> print(select('person', joins=left_join('detail', using=('person_id', ))))
    SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")

.. py:function:: right_join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``RIGHT JOIN ...`` .

    >>> print(select('person', joins=right_join('detail', using=('person_id', ))))
    SELECT * FROM "person" RIGHT JOIN "detail" USING ("person_id")

.. py:function:: cross_join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``CROSS JOIN ...`` .

    >>> print(select('person', joins=cross_join('detail')))
    SELECT * FROM "person" CROSS JOIN "detail"
