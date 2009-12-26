from math import log
from Persistent.Array.fixed_array import FixedArray
from Persistent import DynamicCollection

class Array(DynamicCollection):

    def __init__(self, data, file_name, file_object=None, address=None):
        data() # Initialize, just in case
        self.data = data
        DynamicCollection.__init__(self, file_name, file_object, address)

    def _create_collection(self, address=None):
        return FixedArray(self.data, None, self.file_object,
                self.initial_allocation, address)

    def _get_array_index(self, index):
        block = (index + self.initial_allocation) / self.initial_allocation
        return int(log(block, 2))

    def _get_relative_index(self, index, array_index):
        if array_index > 0:
            return index - self.initial_allocation*((2**array_index)-1)
        return index

    def __setitem__(self, index, data):
        array_index    = self._get_array_index(index)
        relative_index = self._get_relative_index(index, array_index)
        if array_index < len(self.collections):
            self.collections[array_index][relative_index] = data
        else:
            self._add_collection()
            # Recurse and try setting again
            self[index] = data

    def __getitem__(self, index):
        array_index    = self._get_array_index(index)
        relative_index = self._get_relative_index(index, array_index)
        if array_index < len(self.collections):
            return self.collections[array_index][relative_index]
        else:
            self._add_collection()
            return self[index]

    def close(self):
        self.file_object.close()
