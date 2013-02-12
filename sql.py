#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SQL(dict):

    @classmethod
    def insert_into(cls, table):
        pass

    @classmethod
    def select(cls, *fields):
        pass

    @classmethod
    def update(cls, table):
        pass

    @classmethod
    def delete_from(cls, table):
        pass

    def __setattr__(self, key, value):
        pass

    def __str__(self):
        pass

if __name__ == '__main__':
    pass
