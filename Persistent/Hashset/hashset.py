from Persistent                   import DynamicCollection
from Persistent.Hashset.fixed_set import FixedSet

class Hashset(DynamicCollection):

    def __init__(self, data, file_name, file_object=None, address=None):
        self.data = data
        DynamicCollection.__init__(self, file_name, file_object, address)

    def _create_collection(self, address=None):
        return FixedSet(self.data, None, self.file_object, self.initial_allocation, address=address)

    def add(self, data):
        if self.collections[-1].set(data) == True:
            return
        self._add_collection()
        self.add(data)

    def get(self, data, default=None):
        for fixed_set in reversed(self.collections):
            result = fixed_set.get(data)
            if result != None:
                return result
        return default

    def __contains__(self, data):
        return self.get(data) != None
