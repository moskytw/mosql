
The Changes
===========

v0.4
----

1. improved the code of :class:`mosql.result.Model`
2. added :attr:`mosql.result.Model.squash_all` for 1:1 table
3. added :meth:`mosql.result.Model.rows` for iterating the rows in a model instance
4. support to access :class:`mosql.result.Model` by row index
5. added :meth:`mosql.result.Model.getcur` for customizing cursor
6. make :meth:`mosql.result.Model.pop` return the row poped now
7. removed :meth:`mosql.result.Model.row` and :meth:`mosql.result.Model.col`

v0.3
----

1. improved the memory usage of :meth:`mosql.result.Model.arrange`.
2. support to use native escape functions (via :mod:`mosql.psycopg2_escape` or :mod:`mosql.MySQLdb_escape`)

v0.2.1
------

1. fixed a bug of :meth:`mosql.result.Model.append`.

v0.2
----

1. :mod:`mosql.result` is totally rewritten, and does **not** provide the
   backward-compatibility. See the doc for more info.
2. :mod:`mosql.common` is renamed as :mod:`mosql.build`.
3. :mod:`mosql.ext` is removed.
4. :func:`mosql.build.insert` uses `set` instead of `pairs_or_columns`.
5. :func:`mosql.build.insert` supports "on duplicate key update" now.
6. :mod:`mosql.select` uses `*` if `select` user passed in is ``None``.
7. MoSQL passed all of the injection tests from `sqlmap <http://sqlmap.org/>`_
   on value and identifier with PostgreSQL and MySQL.

v0.1.6
------

1. :mod:`mosql.util` is faster (1.35x~1.7x) after rewriting.
2. supports to delimit the identifier (for avoiding injection from identifier).
3. supports arbitrary SQL statements by :class:`mosql.util.raw`.
4. supports to customize parameter name of prepared statement by
   :class:`mosql.util.param`.
5. :mod:`mosql.ext` is deprecated now. Use :mod:`mosql.common` instead.

v0.1.5
------

1. refined the :py:mod:`mosql.mysql`.
2. both PostgreSQL and MySQL with MoSQL passed all of the injection tests from
   `sqlmap <http://sqlmap.org/>`_.

v0.1.4
------

1. fixed the dumped value of datetime, date and time

v0.1.3
------

1. reverted the #3 changes in the previous version.
2. make the rows order by nothing by default.

v0.1.2
------

1. added the :py:mod:`mosql.mysql`.
2. make :py:meth:`mosql.result.Model.seek` respect the arguments from users.
3. make :py:attr:`~mosql.result.Model.group_by` use the value of
   :py:attr:`~mosql.result.Model.identify_by`, by default.
4. stop using the value of :py:attr:`~mosql.result.Model.identify_by` as
   :py:attr:`~mosql.result.Model.order_by`.

v0.1.1
------

1. added the :py:mod:`mosql.json`.
2. added the :py:meth:`mosql.result.Model.customize`.
3. supports using attribute to access :py:class:`~mosql.result.Model`.
4. allows customizing insert, select, update and delete by the class methods of
   a :py:class:`~mosql.result.Model`.
5. respects the ``column_names`` when do a select.
6. fixed the wrong sql without specifying ``identify_by``.
7. fixed the SQL dumped with None. (issue `#1
   <https://github.com/moskytw/mosql/issues/1>`_)
