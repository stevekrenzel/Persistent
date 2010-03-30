###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

import os
from time import time
from Persistent import Array, Hashset, Hashmap, Data, IntegerProperty

class User(Data):
    id     = IntegerProperty(key=True)
    age    = IntegerProperty()

def test(container, setter, getter):
    db    = "test.db"
    size  = 174000
    users = container(User, db)

    t = time()
    for i in xrange(size):
        setter(users, i)
    t = time() - t
    print "Writing: %d" % (size / t)

    t = time()
    for i in xrange(size):
        user = getter(users, i)
        if user.age != i:
            users.close()
            os.remove(db)
            raise Exception("FAILED: %d %s" % (i, str(user)))
    t = time() - t
    print "Reading: %d" % (size / t)

    users.close()
    os.remove(db)

print "\nArray"
def setter(x, y):
    x[y] = User(id=y, age=y)
test(Array, setter, lambda x, y: x[y])

print "\nHashset"
def setter(x, y):
    x.add(User(age=y))
test(Hashset, setter, lambda x, y: x.get(User(age=y)))

print "\nHashmap"
def setter(x, y):
    x[y] = y
test(Hashmap, setter, lambda x, y: x.get(User(id=y)))
