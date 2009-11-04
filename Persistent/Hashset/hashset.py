###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from Persistent                   import DynamicCollection
from Persistent.Hashset.fixed_set import FixedSet

class Hashset(DynamicCollection):

    def __init__(self, format, file_object, initial_allocation=1024, address=None):
        self.format = format
        DynamicCollection.__init__(self, file_object, initial_allocation, address)

    def __create_collection__(self, address=None):
        return FixedSet(self.format, self.file_object, self.initial_allocation, address=address)

    def set(self, *data):
        if self.collections[-1].set(*data) == True:
            return
        self.add_collection()
        self.set(*data)

    def get(self, data, default=None):
        for a in reversed(self.collections):
            b = a.get(data)
            if b != None:
                return b
        return default

    def __contains__(self, data):
        return self.get(data) != None
