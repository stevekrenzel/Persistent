###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from Persistent import PersistentMap

class IntegerIntegerMap(PersistentMap):
    def __init__(self, file_object, map_size, address=None, key_ints=1, val_ints=1):
        PersistentMap.__init__(self, file_object, "I"*key_ints, "I"*val_ints, map_size, address=address)
