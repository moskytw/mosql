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
                id integer,
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
        print q

        self.cursor.execute(q, {'person_id': 'mosky'})


if __name__ == '__main__':
    # hack the path to run the test in test folder
    # correct way should be add a run test script in the module root.
    import sys
    sys.path.insert(0, "..")
    reload(mosql)

    unittest.main()

