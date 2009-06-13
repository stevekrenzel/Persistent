###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from Persistent import KeyValueList

class StringStringList(KeyValueList):
    """The StringStringList is a key-value list where both the key and value 
    is a string.
    
    Note: All operations on this take O(N) time
    TODO: We should be able to have some kind of primitive string node, also
    when we fix lists to use addresses at the start of the node rather than
    the end, we need to update the self.head.address seeks in here.

    """
    def __init__(self, file_object, address=None):
        """We create a KeyValueList that stores two ints, the length of the
        key string, and the length of the value string.

        """
        KeyValueList.__init__(self, file_object, "I", "I", address)

    def set(self, key, value):
        """Setting a key/value pair actually just deletes the original node
        with our key, and appends a new node that uses the key. If delete
        doesn't find a node with our key, it doesn't do anything.

        Note that this means once a node is in a file, we never remove that
        data or reuse that space.

        """
        KeyValueList.delete(self, key)
        KeyValueList.append(self, len(key), len(value), post_data = key + value)

    def __iter__(self):
        """Iterates through all of the nodes and returns the key and value
        associated with the respective node.

        """
        # The head node is cached in the list instance and the file pointer
        # may have moved around since the time that we created the list, so we
        # aren't guaranteed that the file pointer will be anywhere. As a
        # result, we seek to the head address to make sure we're there.
        if self.head:
            self.file_object.seek(self.head.address)
        for node in self.node_iter():
            yield self.__get_key_val__(node)

    def items(self):
        """Iterates through all of the nodes and returns the node and key
        associated with the respective node.

        """
        # The head node is cached in the list instance and the file pointer
        # may have moved around since the time that we created the list, so we
        # aren't guaranteed that the file pointer will be anywhere. As a
        # result, we seek to the head address to make sure we're there.
        if self.head:
            self.file_object.seek(self.head.address)
        return KeyValueList.items(self)

    def __get_key_val__(self, node):
        """Assumes that the file pointer is sitting at the end of the node,
        at which point we read the bytes for the key and value which are
        appended directly after the node.

        """
        key_len, val_len = KeyValueList.__get_key_val__(self, node)
        data = self.file_object.read(key_len + val_len)
        key = data[:key_len]
        val = data[key_len:]
        return key, val
