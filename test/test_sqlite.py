import mosql
from mosql.query import insert
from mosql.util import param
import sqlite3
import unittest

class TestMosqlSqlite3(unittest.TestCase):
    def setUp(self):
        self.connect = sqlite3.connect(":memory:")
        self.cursor = self.connect.cursor()

        self.cursor.executescript("""
            create table if not exists person(
                id integer integer primary key,
                person_id text,
                name text
            );
        """)

    def test_insert(self):
        from mosql.query import insert
        q = insert('person', {
            "person_id": "mosky",
            "name": "Mosky Liu"
        })

        self.cursor.execute(q)
        self.connect.commit()

    def test_update(self):
        from mosql.query import update
        q = update('person', {'person_id': 'mosky'}, {'name': 'Mosky Liu'})

        self.cursor.execute(q)
        self.connect.commit()

    def test_delete(self):
        from mosql.query import delete
        q = delete('person', {'person_id': 'mosky'})

        self.cursor.execute(q)
        self.connect.commit()

    def test_select(self):
        from mosql.query import select
        q = select('person', {'person_id': 'mosky'})

        qs = self.cursor.execute(q)

        import mosql.sqlite
        q =  select('person', {'person_id': param('person_id')})
        # print q

        self.cursor.execute(q, {'person_id': 'mosky'})
        self.connect.commit()

    def test_escape_native(self):
        eval_string =  "\n\r\\\"\x1A\b\t"
        self.cursor.execute("insert or replace into person(id, person_id, name) values(?, ?,?)", (1, 'mosqk', eval_string))
        self.connect.commit()

        self.cursor.execute("select name from person where id = ?", (1, ))
        v = self.cursor.fetchall()

        assert v[0][0] == eval_string

    def test_escape(self):
        eval_string =  "\n\r\\\"\x1A\b\t"
        from mosql.query import insert
        q = insert('person', {
            "id": 1,
            "person_id": "mosky",
            "name": eval_string
        })

        # print q
        self.cursor.execute(q)
        self.connect.commit()

        self.cursor.execute("select name from person where id = ?", (1,))
        v = self.cursor.fetchall()

        assert v[0][0] == eval_string


if __name__ == '__main__':
    # hack the path to run the test in test folder
    # correct way should be add a run test script in the module root.
    import sys
    sys.path.insert(0, "..")
    reload(mosql)

    unittest.main()

