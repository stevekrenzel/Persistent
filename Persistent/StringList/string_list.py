###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
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
