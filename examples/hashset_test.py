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
from Persistent import Hashset
from Persistent.Data.test import Data
from Persistent.Data.property import IntegerProperty

class User(Data):
    id     = IntegerProperty()
    age    = IntegerProperty()
    zindex = IntegerProperty()

seed(4)
db    = "set_test.db"
size  = 100000
rands = list(set([randint(0, 50000000) for i in xrange(size)]))
users = Hashset(User, db)

t = time()
for i in rands:
    user = users.newUser()
    user.age = i
    users.set(user)
print time() - t

t = time()
for i in rands:
    user     = users.newUser()
    user.age = i
    nuser = users.get(user)
    if nuser.age != i:
        print nuser
print time() - t
users.close()

users = Hashset(User, db)
t = time()
for i in rands:
    user     = users.newUser()
    user.age = i
    nuser = users.get(user)
    if nuser.age != i:
        print nuser
print time() - t
users.close()

os.remove(db)
