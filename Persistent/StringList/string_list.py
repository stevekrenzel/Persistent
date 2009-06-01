from Persistent import IntegerList

class StringList(IntegerList):
    def __init__(self, file_object, address=None):
        self.file_object = file_object
        # We make an integer list that stores two ints. One
        # int for the address of the string, and one int for
        # the length of the string
        IntegerList.__init__(self, file_object, 2, address)

    def append(self, value):
        self.file_object.seek(0, 2)
        address = self.file_object.tell()
        length  = len(value)
        self.file_object.write(value)
        IntegerList.append(self, address, length)

    def __iter__(self):
        for node in self.node_iter():
            val = node.get_value()
            address, length = val[0], val[1]
            self.file_object.seek(address)
            yield self.file_object.read(length) 
