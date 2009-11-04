###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from math                         import log
from Persistent.Array.fixed_array import FixedArray
from Persistent                   import DynamicCollection

class Array(DynamicCollection):

    def __init__(self, format, file_object, initial_allocation=1024, address=None):
        self.format          = format
        self.base_allocation = initial_allocation
        DynamicCollection.__init__(self, file_object, initial_allocation, address)

    def __create_collection__(self, address=None):
        return FixedArray(self.format, self.file_object, self.initial_allocation, address)

    def __get_array_index__(self, index):
        return int(log((index + self.base_allocation)/self.base_allocation, 2))

    def __get_relative_index(self, index, array_index):
        a, i, n = array_index, index, self.base_allocation
        return i - n*((2**a)-1) if a > 0 else i

    def __setitem__(self, index, data):
        array_index    = self.__get_array_index__(index)
        relative_index = self.__get_relative_index(index, array_index)
        if array_index < len(self.collections):
            self.collections[array_index][relative_index] = data
        else:
            self.add_collection()
            self[index] = data

    def __getitem__(self, index):
        array_index    = self.__get_array_index__(index)
        relative_index = self.__get_relative_index(index, array_index)
        if array_index < len(self.collections):
            return self.collections[array_index][relative_index]
        else:
            self.add_collection()
            return self[index]

def main():
    import os
    from random import randint
    from time import time

    filename = "vector_test.db"
    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()

    db     = open(filename, "r+b")
    format = "I:age"
    size   = 100
    num    = 20000
    vector = Array(format, db)
    nums   = [randint(0, 100) for i in xrange(num)]

    t = time()
    for i, e in enumerate(nums):
        vector[i]["age"] = e
    print time() - t

    t = time()
    for i, e in enumerate(nums):
        if vector[i]["age"] != e:
            print "Shit"
    print time() - t

    db.close()
    db     = open(filename, "r+b")
    vector = Array(format, db, address=0)
    t = time()
    for i, e in enumerate(nums):
        if vector[i]["age"] != e:
            print "Shit"
    print time() - t
    db.close()
    os.remove(filename)

if __name__ == "__main__":
    main()
