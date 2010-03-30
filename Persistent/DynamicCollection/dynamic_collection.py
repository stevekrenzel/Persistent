import os
from struct import pack, unpack, calcsize

class DynamicCollection:
    """ DynamicCollection simply centralizes some of the common logic between
    collections that dynamically resize. It is used by Array, Hashset, and
    Hashmap.

    TODO: Add proper tests to this class. In all fairness though most of the
    functionality is already tested by the other classes that implement it.

    """

    def __init__(self, data, file_name=None, file_object=None, address=None):
        """ Initializes a new dynamic collection.

        Data is the class for the elements that will be stored in this collection.

        File_name is the name of the file that contains, or will contain,
        the collection. This is an optional parameter, but must be specified
        if a file_object isn't specified.

        File_object is the file object that contains, or will contain,
        the collection. This is an optional parameter, but must be specified
        if a file_name isn't specified.

        Address is the address in the file that the collection starts at. If
        no address is supplied, space for a new collection is allocated at the
        end of the file.

        TODO add "bytes" argument for loading through Data objects, set initial allocation too

        """
        # Data objects have certain varibles, such as the size of the object,
        # initialized the first time the constructoris called. Here we force
        # these variables to be intiialized.
        data()
        self.data = data
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
        # TODO make this a linked list instead of array[32]
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
            # TODO This just seeks and reads the size of each collection. We could
            # store this locally to cut down on that seek time
            self.collections = [self._create_collection(address=i)
                for i in self.pointers if i > -1]

    def _add_collection(self):
        """ Adds an additional collection to the list of collections. """

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

    def _create_collection(self, address=None):
        """ Creates a new fixed size collection depending upon what the child
        set self.fixed_collection to. For arrays this would be FixedArray, for
        sets it'd be FixedSet.

        It also doubles the size of the allocation, so that the new collection
        is twice as large as the previous one.

        """
        allocation = (2**len(self.collections)) * self.initial_allocation
        fixed = self.fixed_collection
        return fixed(data=self.data, file_name=None, file_object=self.file_object, allocation=allocation, address=address)

    def close(self):
        """ Closes the associated file object for this collection. """
        self.file_object.close()
