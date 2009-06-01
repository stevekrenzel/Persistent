#!/usr/bin/python
import os
from itertools import izip
from Persistent import IntegerList

######################################################################
# Now we'll run through a couple simple use cases for 
# using the persistent list
######################################################################
filename = "test.db"

# Create the file if it doesn't exist
if not os.path.exists(filename): 
    open(filename, 'w').close()

db = open(filename, "r+b")

######################################################################
# Create three individual integer lists, but all will be stored in the
# same file. One list will store even numbers, one will store
# odd numbers, and one will store tuples of (even, odd) pairs.
######################################################################
evenList    = IntegerList(db)
oddList     = IntegerList(db)
evenOddList = IntegerList(db, 2) # Stores 2 ints instead of 1

######################################################################
# First we'll populate our even and odd lists
######################################################################
for i in xrange(10):
    if i%2 == 0:
        evenList.append(i)
    else:
        oddList.append(i)

######################################################################
# We zip the two lists together, and populate our third list
######################################################################
for i in izip(evenList, oddList):
    evenOddList.append(*i)

######################################################################
# Oh no! We closed the file! Wherever are our lists!?
######################################################################
db.close()

######################################################################
# As long as we have the address of the head node in the list, we're
# okay. We need the head address because the node can be anywhere in
# the file.
######################################################################
evenHead    = evenList.head.address
oddHead     = oddList.head.address
evenOddHead = evenOddList.head.address

######################################################################
# Open the file again, we're going to prove those lists are in there
# somewhere.
######################################################################
db = open(filename, "r+b")

######################################################################
# We create the lists again, but this time specify an address
######################################################################
evenList    = IntegerList(db,    address=evenHead)
oddList     = IntegerList(db,    address=oddHead)
evenOddList = IntegerList(db, 2, address=evenOddHead)

######################################################################
# Here's what all of our hard work produced. Whew....
######################################################################
print evenList
print oddList
print evenOddList

######################################################################
# k thx bai
######################################################################
db.close()
