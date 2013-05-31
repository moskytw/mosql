#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import MySQL

class Detail(MySQL):
    table      = 'detail'
    arrange_by = ('person_id', 'key')
    squashed   = set(arrange_by)
    ident_by   = ('detail_id', )
    clauses    = dict(order_by=arrange_by+ident_by)

if __name__ == '__main__':

    # if you want to see the SQLs it generates
    #Detail.dump_sql = True

    print "# The Model of Mosky's Emails"
    print
    mosky_emails = Detail.where(person_id='mosky', key='email')
    print mosky_emails
    print

    print "# Show the Mosky's Emails"
    print
    print mosky_emails.val
    print

    print '# Show the Rows'
    print
    for row in mosky_emails.rows():
        print row
    print

    print '# Remove the First Email, and Show the Row Removed'
    print
    removal_email = mosky_emails.pop(0)
    mosky_emails.save()
    print removal_email
    print

    print "# Re-Select the Mosky's Emails"
    print
    print Detail.where(person_id='mosky', key='email')
    print

    print '# Add the Email Just Removed Back, and Re-Select'
    print
    mosky_emails.append(removal_email)
    mosky_emails.save()
    print Detail.where(person_id='mosky', key='email')
    print

    print '# Add a New Email for Andy, and Remove It'
    print
    andy_emails = Detail.where(person_id='andy', key='email')
    # The squashed columns are auto filled, and the other columns you ignored
    # are filled SQL's DEFAULT.
    andy_emails.append({'val': 'andy@hiscompany.com'})
    andy_emails.save()
    print andy_emails
    print

    # But because the `detail_id` is unknown, so you can't remove it.
    #andy_emails.pop() # -> ValueError

    # You need to re-select.
    # TODO: support using returning to fetch the updated value
    andy_emails = Detail.where(person_id='andy', key='email')
    andy_emails.pop()
    andy_emails.save()
    print andy_emails
    print

    from person import Person

    d = {'person_id': 'tina', 'name': 'Tina Dico'}
    Person.insert(d, on_duplicate_key_update=d)

    print '# Create Emails for Tina'
    print
    tina_emails = Detail.new({'person_id': 'tina', 'key': 'email'})
    # or use ``Detail.default(person_id='tina', key='email')`` for short
    tina_emails.append({'val': 'tina@whatever.com'})
    tina_emails.append({'val': 'tina@whatever2.com'})
    tina_emails.save()
    print tina_emails
    print

    print '# Remove Tina'
    print
    tina_emails = Detail.where(person_id='tina', key='email')
    tina_emails.clear()
    tina_emails.save()
    print tina_emails
    print

    Person.delete(d)
