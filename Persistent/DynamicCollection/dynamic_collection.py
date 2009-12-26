import os
from struct import pack, unpack, calcsize

class DynamicCollection:

    def __init__(self, file_name, file_object, address=None):
        if file_name != None:
            if not os.path.exists(file_name):
                # Create the file if it doesn't exist
                open(file_name, 'w').close()
            elif address == None:
                # If the file exists already and no address is supplied 
                address = 0
            file_object = open(file_name, 'r+b')
        self.file_object        = file_object
        self.initial_allocation = 1024
        self.pointers_format    = "q" * 32
        self.pointers           = [-1] * 32
        self.address            = address
        self.collections        = []

        # We allocate space at the end of the file if there is no address
        if self.address == None:
            # Seek to the end of the file and record the address
            self.file_object.seek(0, 2)
            self.address = self.file_object.tell()

            # Write the pointers
            self.file_object.write(pack(self.pointers_format, *self.pointers))

            # Allocate the first array
            self._add_collection()
        else:
            # Seek to the pointers
            self.file_object.seek(self.address)

            # Read in the pointers
            self.pointers = list(unpack(self.pointers_format,
                self.file_object.read(calcsize(self.pointers_format))))

            # Load collections
            self.collections = [self._create_collection(address=i)
                for i in self.pointers if i > -1]

    def _add_collection(self):
        # Find the position of the next null pointer
        position = self.pointers.index(-1)

        # We allocate the array
        new_collection = self._create_collection()

        # Update our pointers and sizes
        self.pointers[position] = new_collection.address

        # Seek to the pointers
        self.file_object.seek(self.address)

        # Write the pointers
        self.file_object.write(pack(self.pointers_format, *self.pointers))

        # Add our new array to our list of arrays
        self.collections.append(new_collection)

        # Each new allocation doubles the size of the previous one
        self.initial_allocation = 2 * self.initial_allocation

    def _create_collection(self, address=None):
        pass

    def close(self):
        self.file_object.close()
