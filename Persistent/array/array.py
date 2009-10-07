###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize
from time import time
from fixed_array import FixedArray

class Array:

    def __init__(self, format, file_object, initial_allocation=1024, address=None):
        self.file_object        = file_object
        self.format             = format
        self.initial_allocation = initial_allocation
        self.cleaned_format     = "".join(i.split(":")[0].strip() for i in format.split(","))
        self.format_size        = calcsize(self.cleaned_format)
        self.pointers_format    = "q" * 32
        self.pointers           = [-1] * 32
        self.address            = address
        self.arrays             = []

        # We allocate space at the end of the file if there is no address
        if self.address == None:
            # Seek to the end of the file and record the address
            self.file_object.seek(0, 2)
            self.address = self.file_object.tell()

            # Write the pointers
            self.file_object.write(pack(self.pointers_format, *self.pointers))

            # Allocate the first array
            self.add_array()
        else:
            # Seek to the pointers
            self.file_object.seek(self.address)

            # Read in the pointers
            self.pointers = list(unpack(self.pointers_format, self.file_object.read(calcsize(self.pointers_format))))

            # Load arrays
            self.arrays = [FixedArray(self.format, self.file_object, address=i) for i in self.pointers if i > -1]

    def add_array(self):
        # Find the position of the next null pointer
        position = self.pointers.index(-1)

        # We allocate the array
        new_array = FixedArray(self.format, self.file_object, self.initial_allocation)

        # Update our pointers and sizes
        self.pointers[position] = new_array.address

        # Seek to the pointers
        self.file_object.seek(self.address)

        # Write the pointers
        self.file_object.write(pack(self.pointers_format, *self.pointers))

        # Add our new array to our list of arrays
        self.arrays.append(new_array)

        # Each new allocation doubles the size of the previous one
        self.initial_allocation = 2 * self.initial_allocation

    def __setitem__(self, index, *values):
        total = 0
        for a in self.arrays:
            diff  = (a.size / self.format_size)
            if index < (total + diff):
                a.__setitem__(index - total, *values)
            total = total + diff
        self.add_array()
        self.__setitem__(index, *values)

    def __getitem__(self, index):
        total = 0
        for a in self.arrays:
            diff  = (a.size / self.format_size)
            if index < (total + diff):
                g = a[index - total]
                return a[index - total]
            total = total + diff
        self.add_array()
        return self.__getitem__(index)

if __name__ == "__main__":
    import os

    filename = "vector_test.db"
    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()

    db     = open(filename, "r+b")
    format = "I:age, 10p:name"
    size   = 1
    num    = 100000
    vector = Array(format, db, initial_allocation = size)
    t = time()
    for i in range(num):
        vector[i]["age"] = i
    print time() - t

    t = time()
    for i in range(num):
        if vector[i]["age"] != i:
            print "OH NO!"
    print time() - t
    db.close()
    db = open(filename, "r+b")
    vector = Array(format, db, address = vector.address)
    t = time()
    for i in range(num):
        if vector[i]["age"] != i:
            print "OH NO!"
    print time() - t
    db.close()
    os.remove(filename)
