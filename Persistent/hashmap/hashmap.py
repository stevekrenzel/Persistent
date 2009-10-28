###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize
from time import time
from fixed_map import FixedMap

class Hashmap:

    def __init__(self, key_format, val_format, file_object, initial_allocation=1024, address=None):
        self.file_object        = file_object
        self.key                = Data(key_format)
        self.key_format         = key_format
        self.val                = Data(val_format)
        self.val_format         = val_format
        self.initial_allocation = initial_allocation
        self.pointers_format    = "q" * 32
        self.pointers           = [-1] * 32
        self.address            = address
        self.maps               = []

        # We allocate space at the end of the file if there is no address
        if self.address == None:
            # Seek to the end of the file and record the address
            self.file_object.seek(0, 2)
            self.address = self.file_object.tell()

            # Write the pointers
            self.file_object.write(pack(self.pointers_format, *self.pointers))

            # Allocate the first array
            self.add_set()
        else:
            # Seek to the pointers
            self.file_object.seek(self.address)

            # Read in the pointers
            self.pointers = list(unpack(self.pointers_format, self.file_object.read(calcsize(self.pointers_format))))

            # Load maps
            self.maps = [FixedMap(self.key_format, self.val_format, self.file_object, address=i) for i in self.pointers if i > -1]

    def add_set(self):
        # Find the position of the next null pointer
        position = self.pointers.index(-1)

        # We allocate the array
        new_set = FixedMap(self.key_format, self.val_format, self.file_object, self.initial_allocation)

        # Update our pointers and sizes
        self.pointers[position] = new_set.address

        # Seek to the pointers
        self.file_object.seek(self.address)

        # Write the pointers
        self.file_object.write(pack(self.pointers_format, *self.pointers))

        # Add our new set to the start of our list of maps
        # We add it first because we want the largest maps searched first
        self.maps = [new_set] + self.maps

        # Each new allocation doubles the size of the previous one
        self.initial_allocation = 2 * self.initial_allocation

    def set(self, key, val):
        if self.maps[0].set(key, val) == True:
            return
        self.add_set()
        self.set(key, val)

    def get(self, key):
        for a in self.maps:
            b = a.get(key)
            if b != None:
                return b
        return None

    def __contains__(self, data):
        return self.get(data) != None

if __name__ == "__main__":
    import os
    from random import randint, seed
    from Persistent import Data
    from time import time
    seed(6)

    filename = "hashmap_test.db"
    rands    = set([randint(0, 50000000) for i in xrange(1000000)])
    data    = []
    for i, e in enumerate(rands):
        k = Data("I:age")
        v = Data("20p:name")
        k["age"] = i
        v["name"] = str(e)
        data.append((k, v))
    del(rands)

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()
    db = open(filename, "r+b")

    hashmap  = Hashmap("I:age", "20p:name", db)

    t = time()
    for k, v in data:
        hashmap.set(k, v)
    print time() - t

    t = time()
    for k, v in data:
        hashmap.get(k)
    print time() - t

    db.close()
    os.remove(filename)
