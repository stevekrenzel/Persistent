###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize
from time import time
from fixed_set import FixedSet

class Hashset:

    def __init__(self, format, file_object, initial_allocation=1024, address=None):
        self.file_object        = file_object
        self.format             = format
        self.initial_allocation = initial_allocation
        self.cleaned_format     = "".join(i.split(":")[0].strip() for i in format.split(","))
        self.format_size        = calcsize(self.cleaned_format)
        self.pointers_format    = "q" * 32
        self.pointers           = [-1] * 32
        self.address            = address
        self.sets               = []

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

            # Load arrays
            self.sets = [FixedSet(self.format, self.file_object, address=i) for i in self.pointers if i > -1]

    def add_set(self):
        # Find the position of the next null pointer
        position = self.pointers.index(-1)

        # We allocate the array
        new_set = FixedSet(self.format, self.file_object, self.initial_allocation)

        # Update our pointers and sizes
        self.pointers[position] = new_set.address

        # Seek to the pointers
        self.file_object.seek(self.address)

        # Write the pointers
        self.file_object.write(pack(self.pointers_format, *self.pointers))

        # Add our new set to the start of our list of sets
        # We add it first because we want the largest sets searched first
        self.sets = [new_set] + self.sets

        # Each new allocation doubles the size of the previous one
        self.initial_allocation = 2 * self.initial_allocation

    def set(self, data):
        for a in self.sets:
            if a.set(data) == True:
                return
        self.add_set()
        print "ADDING SET"
        self.set(data)

    def get(self, data):
        for a in self.sets:
            b = a.get(data)
            if b != None:
                return b
        return None

    def __contains__(self, data):
        return self.get(data) != None

if __name__ == "__main__":
    import os
    from random import randint, seed
    from Persistent import Data
    seed(6)

    filename = "hashset_test.db"
    rands    = set([randint(0, 50000000) for i in xrange(30)])
    format   = "I:age, 20p:name"

    d         = Data(format)
    d["age"]  = 9
    d["name"] = "Steve"

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()
    db = open(filename, "r+b")

    hashset  = Hashset(format, db, 1)
    for i, e in enumerate(rands):
        d["age"] = e
        hashset.set(d)
        print "SET ", d

    print "-----"
    for i, e in enumerate(rands):
        d["age"] = e
        print hashset.get(d)

    db.close()
    os.remove(filename)
