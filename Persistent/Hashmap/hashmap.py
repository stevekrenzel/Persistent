###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from Persistent                   import Hashset
from Persistent.Hashmap.fixed_map import FixedMap

class Hashmap(Hashset):

    def __init__(self, key_format, val_format, file_object, initial_allocation=1024, address=None):
        self.key_format = key_format
        self.val_format = val_format
        Hashset.__init__(self, None, file_object, initial_allocation, address)

    def __create_collection__(self, address=None):
        return FixedMap(self.key_format, self.val_format, self.file_object, self.initial_allocation, address=address)
