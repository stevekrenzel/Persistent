###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from Persistent import Data
from time import time
from struct import pack, unpack, calcsize

class Array:

    def __init__(self, file_object, format, allocation=1024, address=None):
        self.file_object     = file_object
        self.format          = format
        self.cleaned_format  = "".join(i.split(":")[0].strip() for i in format.split(","))
        self.format_size     = calcsize(self.cleaned_format)
        self.size            = allocation*self.format_size
        self.address         = address

        # We allocate space at the end of the file if there is no address
        if self.address == None:
            # Seek to the end of the file and record the address
            self.file_object.seek(0, 2)
            self.address = self.file_object.tell()

            # Write how big this array is
            self.file_object.write(pack("q", self.size))

            # Allocate the space for the elements
            self.__allocate_space__(self.size)
        else:
            # Seek to the start of the array
            self.file_object.seek(self.address)

            # Set the size of the array
            self.size = unpack("q", self.file_object.read(calcsize("q")))

    def __allocate_space__(self, size):
        # We write half a megabyte at a time
        block_size = 512 * 1024

        # We create a block of data filled with invalid addresses
        zeroed_block  = chr(0) * block_size

        # Write the blocks to disk
        for i in xrange(size / block_size):
            self.file_object.write(zeroed_block)

        # The last block won't likely be a full block, so we create a
        # special block for the last one.
        zeroed_block = chr(0) * (size % block_size)
        self.file_object.write(zeroed_block)

    def __setitem__(self, index, *values):
        d = Data(self.file_object, self.format, self.__get_address__(index))
        d.set(*values)

    def __getitem__(self, index):
        return Data(self.file_object, self.format, self.__get_address__(index))

    def __get_address__(self, index):
        return self.address + calcsize("q") + (index * self.format_size)

if __name__ == "__main__":
    import os

    filename = "array_test.db"
    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()

    db     = open(filename, "r+b")
    format = "I:age, 20s:name"
    size   = 100
    array  = Array(db, format, allocation = size)
    for i in range(size):
        array[i]["age"] = i + 1
    for i in range(size):
        if array[i]["age"] != i + 1:
            print "Oh no!"
    # TODO hold onto elements for scenarios like this
    db.close()
    db = open(filename, "r+b")
    array  = Array(db, format, address = array.address)
    for i in range(size):
        if array[i]["age"] != i + 1:
            print "Oh no!"
    db.close()
    os.remove(filename)
