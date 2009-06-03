###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from Persistent import PersistentList

class IntegerList(PersistentList):
    def __init__(self, file_object, number_of_ints=1, address=0):
        PersistentList.__init__(self, file_object, "I"*number_of_ints,
                address=address)
