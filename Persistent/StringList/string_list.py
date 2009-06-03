from Persistent import IntegerList

class StringList(IntegerList):
    def __init__(self, file_object, address=None):
        self.file_object = file_object
        IntegerList.__init__(self, file_object, 1, address)

    def append(self, value):
        IntegerList.append(self, len(value), post_data=value)

    def __iter__(self):
        for node in self.node_iter():
            self.file_object.seek(node.address)
            yield self.file_object.read(node.get_value()) 
