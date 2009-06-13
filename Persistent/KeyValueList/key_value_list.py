###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from struct import unpack, calcsize
from Persistent import PersistentList

class KeyValueList(PersistentList):
    """The KeyValueList is simply a linked list of unique keys and associated
    values. It supprts keys and values following any standard struct format.

    """
    def __init__(self, file_object, key_format, val_format, address=None):
        """Initializes the KeyValueList. """

        self.file_object  = file_object
        self.key_format   = key_format
        self.key_size     = calcsize(key_format) 
        self.val_format   = val_format
        self.val_size     = calcsize(val_format) 
        PersistentList.__init__(self, file_object, key_format + val_format, address)

    def set(self, key, value, post_data=None):
        """Setting a key/value pair actually just deletes the original node
        with our key, and appends a new node that uses the key. If delete
        doesn't find a node with our key, it doesn't do anything.

        Note that this means once a node is in a file, we never remove that
        data or reuse that space.

        """
        PersistentList.delete(self, key)
        PersistentList.append(self, key, value, post_data=post_data)

    def get(self, key):
        """Finds the key in the list and returns the associated value. If the
        key isn't found, None is returned."""
        for new_key, new_val in self:
            if key == new_key:
                return new_val

    def __get_key_val__(self, node):
        """Unpacks the raw bytes of the node into the key and value
        components. If either of these are singular values, it will
        return the single value inside it's respective tuple, rather than
        a tuple with one element in it.

        """
        bytes = node.get_bytes()
        key   = unpack(self.key_format, bytes[:self.key_size])
        val   = unpack(self.val_format, bytes[self.key_size: self.key_size + self.val_size])
        if len(key) == 1:
            key = key[0]
        if len(val) == 1:
            val = val[0]
        return (key, val)

    def __iter__(self):
        """Iterates through all of the nodes and returns the key and value
        associated with the respective node.

        """
        for node in self.node_iter():
            yield self.__get_key_val__(node)

    def items(self):
        """Iterates through all of the nodes and returns the node and key
        associated with the respective node.

        """
        for node in self.node_iter():
            key, val = self.__get_key_val__(node)
            yield node, key
