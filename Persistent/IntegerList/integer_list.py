###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from Persistent import PersistentList

class IntegerList(PersistentList):
    """The IntegerList is a linked list where each node stores the value of a
    specified number of ints. For instance, we could make an IntegerList where
    each node stores two ints. As we traverse the list, each value would then
    be a pair of ints instead of a single int.

    Note that a single int is returned as just that int, whereas multiple ints
    are returned in a tuple.

    """
    def __init__(self, file_object, number_of_ints=1, address=None):
        PersistentList.__init__(self, file_object, "I"*number_of_ints,
                address=address)
