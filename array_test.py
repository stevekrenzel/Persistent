###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

import os
from time import time
from Persistent import Array
from Persistent.Data.test import Data
from Persistent.Data.property import IntegerProperty

class User(Data):
    id     = IntegerProperty()
    age    = IntegerProperty()
    zindex = IntegerProperty()

db    = "array_test.db"
size  = 10
users = Array(User, db)

t = time()
for i in range(size):
    user = users[i]
    user.age    = i
    user.commit()
print time() - t

t = time()
for i in range(size):
    user = users[i]
    print user
print time() - t
users.close()

users = Array(User, db)
t = time()
for i in range(size):
    user = users[i]
    print user
print time() - t
users.close()

os.remove(db)
