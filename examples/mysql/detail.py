#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import MySQL

class Detail(MySQL):
    clauses = dict(table='detail')
    arrange_by = ('person_id', 'key')
    squashed = arrange_by
    ident_by = ('detail_id', )

if __name__ == '__main__':

    from pprint import pprint

    print '# arrange entire table'
    for detail in Detail.arrange():
        print detail
    print


    print '# modified an email'

    mosky_detail = Detail.select(where={'person_id': 'mosky', 'key': 'email'})

    # you have to use this form to make model remeber the changes
    mosky_detail['val', 0] = 'this email is modified 1'
    mosky_detail['val', 0] = 'this email is modified 2'
    mosky_detail['val', 0] = 'this email is modified'
    mosky_detail.save()

    # re-select to ensure the data modified is saved to db
    mosky_detail = Detail.select(where={'person_id': 'mosky', 'key': 'email'})
    print 'mails:     ', mosky_detail.val
    print 'first mail:', mosky_detail.val[0]

    print


    print '# append'

    mosky_detail = Detail.select(where={'person_id': 'mosky', 'key': 'email'})
    mosky_detail.append({'val': 'it is the new email'})
    mosky_detail.save()

    mosky_detail = Detail.select(where={'person_id': 'mosky', 'key': 'email'})
    print 'mails:', mosky_detail.val

    print


    print '# pop 0'
    mosky_detail = Detail.select(where={'person_id': 'mosky', 'key': 'email'})
    mosky_detail.pop(0)
    mosky_detail.save()

    mosky_detail = Detail.select(where={'person_id': 'mosky', 'key': 'email'})
    print 'mails:', mosky_detail.val

    print
