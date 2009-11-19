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

    def __init__(self, data, file_name, file_object=None, allocation=1, address=None):
        self.data = data
        DynamicCollection.__init__(self, file_name, file_object, allocation, address)

    def __create_collection__(self, address=None):
        return FixedSet(self.data, None, self.file_object, self.initial_allocation, address=address)

    def add(self, data):
        if self.collections[-1].set(data) == True:
            return
        self.add_collection()
        self.add(data)

    def get(self, data, default=None):
        for i, a in enumerate(reversed(self.collections)):
            b = a.get(data)
            if b != None:
                return b
        return default

    def __contains__(self, data):
        return self.get(data) != None
