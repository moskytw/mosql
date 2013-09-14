The Common Queries --- :mod:`mosql.query`
=========================================

This module provides the common :class:`~mosql.util.Query` instances for you.

If you want to build you own, there are all basic bricks you need -
:doc:`/util`.

.. note::

    If you are using non-standard SQL, such as MySQL, you need to patch the
    :mod:`mosql.util`. For MySQL, an official patch is here - :doc:`/mysql`.

.. versionadded:: v0.6

.. py:module:: mosql.query

.. testsetup::

    from mosql.query import select, insert, update, delete
    from mosql.query import join, left_join, right_join, cross_join
    from mosql.util import param, ___, raw

.. py:function:: select(table=None, where=None, **clause_args)

    It generates the SQL statement, ``SELECT ...`` .

    The following usages generate the same SQL statement.

    >>> print select('person', {'person_id': 'mosky'})
    SELECT * FROM "person" WHERE "person_id" = 'mosky'

    >>> print select('person', (('person_id', 'mosky'), ))
    SELECT * FROM "person" WHERE "person_id" = 'mosky'

    It also can handle the dot in an identifier:

    >>> print select('person', select=('person.person_id', 'person.name'))
    SELECT "person"."person_id", "person"."name" FROM "person"

    >>> print select('table', {'custom_param': param('my_param'), 'auto_param': param, 'using_alias': ___})
    SELECT * FROM "table" WHERE "auto_param" = %(auto_param)s AND "using_alias" = %(using_alias)s AND "custom_param" = %(my_param)s

    The prepare statement is also available with :class:`mosql.util.param`:

    >>> print select('table', {'custom_param': param('my_param'), 'auto_param': param, 'using_alias': ___})
    SELECT * FROM "table" WHERE "auto_param" = %(auto_param)s AND "using_alias" = %(using_alias)s AND "custom_param" = %(my_param)s

    You can also specify the ``group_by``, ``having``, ``order_by``, ``limit``
    and ``offset`` in the keyword arguments. Here are some examples:

    >>> print select('person', {'name like': 'Mosky%'}, group_by=('age', ))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' GROUP BY "age"

    >>> print select('person', {'name like': 'Mosky%'}, order_by=('age', ))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"

    >>> print select('person', {'name like': 'Mosky%'}, order_by=('age desc', ))
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC

    >>> print select('person', {'name like': 'Mosky%'}, order_by=('age ; DROP person; --', ))
    Traceback (most recent call last):
        ...
    OptionError: this option is not allowed: '; DROP PERSON; --'

    .. seealso ::
        The options allowed --- :attr:`mosql.util.allowed_options`.

    >>> print select('person', {'name like': 'Mosky%'}, limit=3, offset=1)
    SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1

    The operators are also supported:

    >>> print select('person', {'person_id': ('andy', 'bob')})
    SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')

    >>> print select('person', {'name': None})
    SELECT * FROM "person" WHERE "name" IS NULL

    >>> print select('person', {'name like': 'Mosky%', 'age >': 20})
    SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'

    >>> print select('person', {"person_id = '' OR true; --": 'mosky'})
    Traceback (most recent call last):
        ...
    OperatorError: this operator is not allowed: "= '' OR TRUE; --"

    .. seealso ::
        The operators allowed --- :attr:`mosql.util.allowed_operators`.

    If you want to use functions, wrap it with :class:`mosql.util.raw`:

    >>> print select('person', select=raw('count(*)'), group_by=('age', ))
    SELECT count(*) FROM "person" GROUP BY "age"

    .. warning ::
        You have responsibility to ensure the security if you use :class:`mosql.util.raw`.

    .. seealso ::
        How it builds the where clause --- :func:`mosql.util.build_where`

.. py:function:: insert(table=None, set=None, **clause_args)

    It generates the SQL statement, ``INSERT INTO ...``.

    The following usages generate the same SQL statement:

    >>> print insert('person', {'person_id': 'mosky', 'name': 'Mosky Liu'})
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    >>> print insert('person', (('person_id', 'mosky'), ('name', 'Mosky Liu')))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    >>> print insert('person', columns=('person_id', 'name'), values=('mosky', 'Mosky Liu'))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu')

    The columns is ignorable:

    >>> print insert('person', values=('mosky', 'Mosky Liu'))
    INSERT INTO "person" VALUES ('mosky', 'Mosky Liu')

    All of the :func:`insert`, :func:`update` and :func:`delete` support ``returning``.

    >>> print insert('person', {'person_id': 'mosky', 'name': 'Mosky Liu'}, returning=raw('*'))
    INSERT INTO "person" ("person_id", "name") VALUES ('mosky', 'Mosky Liu') RETURNING *

    The MySQL-specific ``ON DUPLICATE KEY UPDATE`` is also supported:

    >>> print insert('person', values=('mosky', 'Mosky Liu'), on_duplicate_key_update={'name': 'Mosky Liu'})
    INSERT INTO "person" VALUES ('mosky', 'Mosky Liu') ON DUPLICATE KEY UPDATE "name"='Mosky Liu'

.. py:function:: update(table=None, where=None, set=None, **clause_args)

    It generates the SQL statement, ``UPDATE ...`` .

    The following usages generate the same SQL statement.

    >>> print update('person', {'person_id': 'mosky'}, {'name': 'Mosky Liu'})
    UPDATE "person" SET "name"='Mosky Liu' WHERE "person_id" = 'mosky'

    >>> print update('person', (('person_id', 'mosky'), ), (('name', 'Mosky Liu'),) )
    UPDATE "person" SET "name"='Mosky Liu' WHERE "person_id" = 'mosky'

    .. seealso ::
        How it builds the where clause --- :func:`mosql.util.build_set`

.. py:function:: delete(table=None, where=None, **clause_args)

    It generates the SQL statement, ``DELETE FROM ...`` .

    The following usages generate the same SQL statement.

    >>> print delete('person', {'person_id': 'mosky'})
    DELETE FROM "person" WHERE "person_id" = 'mosky'

    >>> print delete('person', (('person_id', 'mosky'), ))
    DELETE FROM "person" WHERE "person_id" = 'mosky'

.. py:function:: join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``... JOIN ...`` .

    >>> print select('person', joins=join('detail'))
    SELECT * FROM "person" NATURAL JOIN "detail"

    >>> print select('person', joins=join('detail', {'person.person_id': 'detail.person_id'}))
    SELECT * FROM "person" INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"

    >>> print select('person', joins=join('detail', using=('person_id', )))
    SELECT * FROM "person" INNER JOIN "detail" USING ("person_id")

    >>> print select('person', joins=join('detail', using=('person_id', ), type='left'))
    SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")

    >>> print select('person', joins=join('detail', type='cross'))
    SELECT * FROM "person" CROSS JOIN "detail"

    .. seealso ::
        How it builds the where clause --- :func:`mosql.util.build_on`

.. py:function:: left_join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``LEFT JOIN ...`` .

    >>> print select('person', joins=left_join('detail', using=('person_id', )))
    SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")

.. py:function:: right_join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``RIGHT JOIN ...`` .

    >>> print select('person', joins=right_join('detail', using=('person_id', )))
    SELECT * FROM "person" RIGHT JOIN "detail" USING ("person_id")

.. py:function:: cross_join(table=None, on=None, **clause_args)

    It generates the SQL statement, ``CROSS JOIN ...`` .

    >>> print select('person', joins=cross_join('detail'))
    SELECT * FROM "person" CROSS JOIN "detail"
