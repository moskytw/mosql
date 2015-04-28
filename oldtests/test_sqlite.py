#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sqlite3
import mosql.sqlite
from mosql.util import param
from mosql.query import insert, select, update, delete, replace
from mosql.db import Database, all_to_dicts

class TestSQLite(unittest.TestCase):

    def setUp(self):

        mosql.sqlite.patch()

        self.db = Database(sqlite3, 'test_sqlite.db')

        with self.db as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS person (
                    person_id TEXT PRIMARY KEY,
                    name      TEXT
                );
            ''')

    def test_insert(self):
        with self.db as cur:
            cur.execute(insert('person', {
                'person_id': 'mosky',
                'name'     : 'Mosky Liu'
            }))
            self.db._conn.rollback()

    def test_replace(self):
        with self.db as cur:
            cur.execute(replace('person', {
                'person_id': 'mosky',
                'name'     : 'Mosky Liu'
            }))
            self.db._conn.rollback()

    def test_update(self):
        with self.db as cur:
            cur.execute(update('person', {'person_id': 'mosky'}, {'name': 'Mosky Liu'}))
            self.db._conn.rollback()

    def test_delete(self):
        with self.db as cur:
            cur.execute(delete('person', {'person_id': 'mosky'}))
            self.db._conn.rollback()

    def test_select(self):
        with self.db as cur:
            cur.execute(select('person', {'person_id': 'mosky'}))
            self.db._conn.rollback()

    def test_param_query(self):

        with self.db as cur:
            cur.execute(
                select(
                    'person',
                    {'person_id': param('person_id')}
                ),
                {'person_id': 'mosky'}
            )
            self.db._conn.rollback()

    def test_native_escape(self):

        # NOTE: \0 will eat all following chars
        strange_name =  '\n\r\\\'\"\x1A\b\t'

        with self.db as cur:

            cur.execute(
                'insert into person (person_id, name) values (?, ?)',
                ('native', strange_name)
            )

            cur.execute('select name from person where person_id = ?', ('native', ))
            name, = cur.fetchone()

            self.db._conn.rollback()

        assert strange_name == name

    def test_escape(self):

        # NOTE: \0 will cause an OperationalError of MoSQL
        strange_name =  '\n\r\\\'\"\x1A\b\t'

        with self.db as cur:

            cur.execute(insert('person', {
                'person_id': 'mosql',
                'name'     : strange_name
            }))

            cur.execute('select name from person where person_id = ?', ('mosql',))
            name, = cur.fetchone()

            self.db._conn.rollback()

        assert strange_name == name

    def test_fetch_all_data(self):
        with self.db as cur:
            cur.execute(insert('person', {
                'person_id': 'mosky',
                'name'     : 'Mosky Liu'
            }))

            cur.execute(select('person'))
            results = all_to_dicts(cur)
            self.db._conn.rollback()
