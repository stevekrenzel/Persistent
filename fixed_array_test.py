###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

import os
from time import time
from random import randint, seed
from Persistent.Array.fixed_array import FixedArray
from Persistent.Data.test import Data
from Persistent.Data.property import IntegerProperty

class User(Data):
    id     = IntegerProperty()
    age    = IntegerProperty()
    zindex = IntegerProperty()

seed(4)
db    = "fixed_array_test.db"
size  = 10
rands = list(set([randint(0, 50000000) for i in xrange(10)]))
users = FixedArray(User, db, allocation=size)

t = time()
for i, r in enumerate(rands):
    user = users.newUser()
    user.age = r
    users[i] = user
    print user
print time() - t

t = time()
for i in range(size):
    user = users[i]
    print user
print time() - t
users.close()

users = FixedArray(User, db)
t = time()
for i in range(size):
    user = users[i]
    print user
print time() - t
users.close()

os.remove(db)
