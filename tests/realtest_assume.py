#!/usr/bin/env python
# -*- coding: utf-8 -*-

from realtest_model import Person, Detail

print "# Find mosky's emails"
detail = Detail.find(person_id='mosky', key='email')
print detail
print

print '# Assume it is existent'
detail = Detail.assume(**detail)
print detail
print

print '# Assume detail_id=10 is existent'
detail = Detail.assume(detail_id=[10])
print detail
print

print '# Pop it'
detail.pop()
print detail
print

print '# Save it'
detail.save()
print detail
print

print '# Revert the change'
detail = Detail.new(person_id='mosky', key='email', detail_id=[10], val=['ubuntu-tw.org'])
print detail
detail.save()
print

print '# Add a person, Topaz Chen'
person = Person.new(person_id='topaz', name=['Topaz Chen'])
print detail
person.save()
print

print "# Assume person_id='topaz' is existent"
person = Person.assume(person_id='topaz')
print person
print

print '# Clear it'
person.clear()
print person
print

print '# Save it'
person.save()
print person
print
