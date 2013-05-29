#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import MySQL

class Detail(MySQL):
    table      = 'detail'
    arrange_by = ('person_id', 'key')
    clauses    = dict(order_by=arrange_by)
    squashed   = set(arrange_by)
    ident_by   = ('detail_id', )

if __name__ == '__main__':

    print '# arrange entire table'
    for detail in Detail.arrange():
        print detail
    print


    print '# modified an email'

    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    backup = mosky_detail.val[0]

    mosky_detail['val'][0] = '<ttypo>'
    mosky_detail.val[0] = '<this email is modified>'
    mosky_detail.save()

    # re-select to check the data is really saved to database
    # the method, where, is also useful
    mosky_detail = Detail.where(person_id='mosky', key='email')
    print 'mails     :', mosky_detail.val
    print 'first mail:', mosky_detail.val[0]

    mosky_detail.val[0] = backup
    mosky_detail.save()
    print 'restored  :', mosky_detail.val[0]

    print


    print '# append'

    mosky_detail = Detail.select({'person_id': 'mosky', 'key': 'email'})
    mosky_detail.append({'val': '<it is the new email>'})
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


    print '# show detail_id and email'
    for row in mosky_detail.rows():
        print row
        print row.detail_id, row.val
