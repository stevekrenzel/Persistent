###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from Persistent import IntegerList

class StringList(IntegerList):
    """ The StringList is a linked list of strings. The actual node of the
    linked list stores only one int, the length of the string. After we write
    the node to disk, we append the string immediately after it.
    
    Even though the string isn't technically a part of the node, it will
    always be right after it. This saves us a disk seek because otherwise we
    would would need to store the length and address of the string and then
    seek to that address before reading it.

    """
    def __init__(self, file_object, address=None):
        IntegerList.__init__(self, file_object, 1, address)

    def append(self, value):
        """When we append a string to the list, we actually just add a new
        int to an integer list. The int is the length of the string. After
        the int node is written to disk, we write the actual string data
        right after it, which is specified in the post_data variable.

        """
        IntegerList.append(self, len(value), post_data=value)

    def __iter__(self):
        """Iterating through the values simply involves iterating through the
        linked list of integers. After we read each integer value, which is
        the length of the string, we assume the file pointer is sitting at
        the end of the node.
        
        Because the file pointer is sitting at the end of the node, and the
        string comes right after the node, we can then just read the number of
        bytes given for the length of the string.
        """

        # The head node is cached in the list instance and the file pointer
        # may have moved around since the time that we created the list, so we
        # aren't guaranteed that the file pointer will be anywhere. As a
        # result, we seek to the head address to make sure we're there.
        if self.head:
            self.file_object.seek(self.head.address)
        for node in self.node_iter():
            # Warning: If *anything* moves the file pointer between the node
            # iterator and reading the string from disk, our assumption about
            # the location of the file pointer no longer holds true and this
            # will break badly. And puppies will die.
            yield self.file_object.read(node.get_value()) 
