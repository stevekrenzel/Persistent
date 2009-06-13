###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from Persistent import PersistentMap, StringStringList

class StringStringMap(PersistentMap):
    """ StringStringMap maps strings to strings. """ 
    def __init__(self, file_object, map_size, address=None):
        PersistentMap.__init__(self, file_object, None, None, map_size, address)

    def __make_list__(self, file_object, key_format, value_format, address=None):
        """ This allows us to use other forms of lists with the map buckets.
        In this case, since strings are variable width we need to use the
        custom StringStringList.
        """
        return StringStringList(file_object, address) 
