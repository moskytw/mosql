#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import psycopg2
from flask import Flask, request, jsonify
from mosql.query import select, left_join

app = Flask(__name__)

conn = psycopg2.connect(host='127.0.0.1', database=os.environ['USER'])

@app.route('/')
def index():
    cur = conn.cursor()
    cur.execute(select(
        'person',
        request.args or None,
        joins = left_join('detail', using=('person_id', )),
    ))
    rows = cur.fetchall()
    cur.close()
    return jsonify(data=rows)

if __name__ == '__main__':

    # Run this script, then try the following urls:
    #
    # 1. http://127.0.0.1:5000/?person_id=mosky
    # 2. http://127.0.0.1:5000/?name=Mosky Liu
    # 3. http://127.0.0.1:5000/?name like=%Mosky%
    #

    app.run(debug=True)
