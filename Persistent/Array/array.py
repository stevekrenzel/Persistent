###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

import os
import pdb
from math import log
from Persistent.Array.fixed_array import FixedArray
from Persistent import DynamicCollection

class Array(DynamicCollection):

    def __init__(self, data, file_name, file_object=None, allocation=1024, address=None):
        data() # Initialize, just in case
        self.data = data
        self.base_allocation = allocation
        DynamicCollection.__init__(self, file_name, file_object, allocation, address)

    def _create_collection(self, address=None):
        return FixedArray(self.data, None, self.file_object, self.initial_allocation, address)

    def _get_array_index(self, index):
        return int(log((index + self.base_allocation)/self.base_allocation, 2))

    def _get_relative_index(self, index, array_index):
        a, i, n = array_index, index, self.base_allocation
        return i - n*((2**a)-1) if a > 0 else i

    def __setitem__(self, index, data):
        array_index    = self._get_array_index__(index)
        relative_index = self._get_relative_index(index, array_index)
        if array_index < len(self.collections):
            self.collections[array_index][relative_index] = data
        else:
            self._add_collection()
            # Recurse and try setting again
            self[index] = data

    def __getitem__(self, index):
        array_index    = self._get_array_index__(index)
        relative_index = self._get_relative_index(index, array_index)
        if array_index < len(self.collections):
            return self.collections[array_index][relative_index]
        else:
            self._add_collection()
            return self[index]

    def close(self):
        self.file_object.close()
