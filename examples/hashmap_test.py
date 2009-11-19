###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

import os
from time import time
from random import randint, seed, shuffle
from Persistent import Hashmap
from Persistent.Data.test import Data
from Persistent.Data.property import IntegerProperty

class User(Data):
    id     = IntegerProperty(key=True)
    age    = IntegerProperty()

seed(4)
db    = "map_test.db"
size  = 174000
users = Hashmap(User, db)
seed(4)
rands = range(size)
shuffle(range(size))

t = time()
for i in rands:
    users[i] = i
print time() - t

t = time()
for i in rands:
    user = users[i]
    if user.age != i:
        print user
print time() - t
users.close()

os.remove(db)
# TODO Make newUser work as expected, is it even necessary? At least make data.commit work
