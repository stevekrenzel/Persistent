###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize

class PersistentNode:
    """The PersistentNode simply stores a value on disk, along with a pointer.
        
    The value must follow the form specified in the value_format variable,
    which is a string specified using the struct string format.

    The pointer is an unsigned integer which stores the address of the
    node that follows it in the linked list. If the pointer value is 0 then
    the node does not link to another node.
    TODO: Change 0 to 2**32 -1
    TODO: Change int to long

    Because the pointer is an unsigned int, it can not be used to point
    past the 4GB point in a file.

    """

    def __init__(self, file_object, value_format, value = None, next = None, address=None):
        """If the adddress is not set, or set to an invalid address, we'll
        create space for a new node in the file_object. If value is not set,
        we zero-out the space, otherwise we write the specified value to disk.
        We also write the address for the next node, if one is provided,
        otherwise we set it to an invalid address.

        If there is an address provided, we simply load that node from disk
        into memory.

        """
        self.file_object = file_object

        # This is a function used to retrieve the next node
        self.node_retriever  = lambda address: PersistentNode(file_object,\
                value_format, address=address)

        # The data format is the value format plus the pointer
        self.data_format = value_format + "I" # Add pointer 
        self.data_length = calcsize(self.data_format)

        # If the address isn't set, we create a new node at the end of the file
        if address == None or address == 0:
            # Zero out the values if a value isn't given
            value = [0]*calcsize(value_format) if value is None else list(value)

            # Make the pointer null if one isn't given 
            value.append(0 if next is None else next.address)
            self.data  = value

            # Seek to the end of the file and write the data
            self.file_object.seek(0, 2)
            self.file_object.write(pack(self.data_format, *self.data))

            # Store the address of the end of the node
            self.address = self.file_object.tell()
        else:
            # If we make it here, a node is already on disk. We just read it.
            self.address = address

            # Seek to the start of the node. We store the address of the end,
            # so we actually seek to the address minus the data length
            self.file_object.seek(self.address - self.data_length)

            # Read the data and save it
            bytes = self.file_object.read(self.data_length)
            self.data  = list(unpack(self.data_format, bytes))

    def set_value(self, *value):
        """This just accepts a series of values that match the value_format,
        appends the pointer, and then stores it to the data var and on disk.
        """
        self.data = list(value) + list(self.get_next_address())
        self.write_data()

    def set_next(self, next):
        """Accepts a node as an argument and sets that node as this node's
        next node in the linked list.

        """
        self.set_next_address(next.address)

    def set_next_address(self, next_address):
        """Whereas set_next() accepts a node as an argument, this accepts the
        actual address of the next node, and set's this node's next node to
        that address.

        """
        #TODO seek to pointer, don't rewrite everything
        # The last value of the data list is the pointer address
        self.data[-1] = next_address or 0
        self.write_data()

    def write_data(self):
        """Writes the current contents of the self.data variable to the disk.

        """
        self.file_object.seek(self.address - self.data_length)
        self.file_object.write(pack(self.data_format, *self.data))

    def get_value(self):
        """Returns the value of the node."""

        # The value if everything up until the pointer (which is the last value)
        value = self.data[:-1]

        # value is a list, but if it only has one element we only return that
        # element (not in a list)
        return value if len(value) > 1 else value[0] 

    def get_next_address(self):
        """Returns the address of the next node."""
        return self.data[-1]

    def get_next(self):
        """Returns the next node that follows this one in the linked list."""
        # If we have a valid address, we retrieve the next node
        if self.get_next_address():
            return self.node_retriever(self.get_next_address())

    def __str__(self):
        """Returns the string representation of the value of this node."""
        return str(self.get_value())

if __name__ == "__main__":
    import doctest
    doctest.testmod()
