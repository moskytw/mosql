#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SQL(dict):

    @classmethod
    def insert(cls, table):
        sql = cls('insert into <table> <columns> values <values>')
        return sql

    @classmethod
    def select(cls, *fields):
        sql = cls('select <columns> from <table> where <condictions> limit <limit> offset <offset>')
        return sql

    @classmethod
    def update(cls, table):
        sql = cls('update <table> set <set> where <condictions>')
        return sql

    @classmethod
    def delete(cls, table):
        sql = cls('delete from <table> where <condictions>')
        return sql

    def __init__(self, template):

        if isinstance(template, str):
            self.template = tuple(template.split(' '))
        else:
            assert hasattr(template, '__iter__'), "argumnet 'template; must be str or iterable"
            self.template = template

    def __setattr__(self, key, value):
        pass

    def __str__(self):
        pass

if __name__ == '__main__':
    pass
