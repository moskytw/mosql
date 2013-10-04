#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Run this script, then try the following urls:
#
# 1. http://127.0.0.1:5000/?person_id=mosky
# 2. http://127.0.0.1:5000/?name=Mosky Liu
# 3. http://127.0.0.1:5000/?name like=%Mosky%
#

import psycopg2
from flask import Flask, request, jsonify
from mosql.query import select, left_join
from mosql.db import Database

db = Database(psycopg2, host='127.0.0.1')

app = Flask(__name__)

@app.route('/')
def index():
    with db as cur:
        cur.execute(select(
            'person',
            request.args or None,
            joins = left_join('detail', using=('person_id', )),
        ))
        return jsonify(data=list(cur))

if __name__ == '__main__':
    app.run(debug=True)
