import os
from struct import pack, unpack, calcsize

class FixedArray:

    def __init__(self, data, file_name=None, file_object=None, allocation=1024, address=None):
        if file_name != None:
            if not os.path.exists(file_name):
                # Create the file if it doesn't exist
                open(file_name, 'w').close()
            elif address == None:
                # If the file exists already and no address is supplied 
                address = 0
            file_object = open(file_name, 'r+b')
        data() # Initialize, just in case
        self.file_object     = file_object
        self.data            = data
        self.size            = allocation*data._size
        self.address         = address
        # TODO Write all construction information to disk

        # We allocate space at the end of the file if there is no address
        if self.address == None:
            # Seek to the end of the file and record the address
            self.file_object.seek(0, 2)
            self.address = self.file_object.tell()

            # Write how big this array is
            self.file_object.write(pack("q", self.size))

            # Allocate the space for the elements
            self._allocate_space(self.size)
        else:
            # Seek to the start of the array
            self.file_object.seek(self.address)

            # Set the size of the array
            self.size = unpack("q", self.file_object.read(calcsize("q")))[0]

    def _allocate_space(self, size):
        # We write half a megabyte at a time
        block_size = 512 * 1024

        # We create a block of data filled with invalid addresses
        zeroed_block  = chr(255) * block_size

        # Write the blocks to disk
        for i in xrange(size / block_size):
            self.file_object.write(zeroed_block)

        # The last block won't likely be a full block, so we create a
        # special block for the last one.
        zeroed_block = chr(255) * (size % block_size)
        self.file_object.write(zeroed_block)

    def __setitem__(self, index, data):
        self.commit(data, index)

    def __getitem__(self, index):
        address = self._get_address(index)
        self.file_object.seek(address)
        bytes = self.file_object.read(self.data._size)
        data = self.data(self, bytes)
        data.fixed_array_index_ = index
        return data

    def commit(self, data, index=None):
        if index == None:
            if hasattr(data, 'fixed_array_index_'):
                index = data.fixed_array_index_
            else:
                raise Exception("Data has no associated index")
        address = self._get_address(index)
        self.file_object.seek(address)
        self.file_object.write(data.unload())

    def _get_address(self, index):
        return self.address + calcsize("q") + (index * self.data._size)

    def close(self):
        self.file_object.close()
