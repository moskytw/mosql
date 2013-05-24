#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import PostgreSQL

class Detail(PostgreSQL):
    table      = 'detail'
    arrange_by = ('person_id', 'key')
    squash_by  = set(arrange_by)
    ident_by   = ('detail_id', )

if __name__ == '__main__':

    print '# arrange entire table'
    for detail in Detail.arrange():
        print detail
    print


    print '# modified an email'

    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    backup = mosky_detail.val[0]

    # you have to use this form to make model remeber the changes
    mosky_detail['val', 0] = 'this email is modified 1'
    mosky_detail['val', 0] = 'this email is modified 2'
    mosky_detail['val', 0] = 'this email is modified'
    mosky_detail.save()

    # re-select to check the data is really saved to database
    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    print 'mails     :', mosky_detail.val
    print 'first mail:', mosky_detail.val[0]

    mosky_detail['val', 0] = backup
    mosky_detail.save()
    print 'restored  :', mosky_detail.val[0]

    print


    print '# append'

    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    mosky_detail.append({'val': 'it is the new email'})
    mosky_detail.save()

    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    print 'mails:', mosky_detail.val

    print


    print '# pop 0'
    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    mosky_detail.pop(0)
    mosky_detail.save()

    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    print 'mails:', mosky_detail.val

    print
