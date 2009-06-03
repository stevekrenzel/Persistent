from struct import pack, unpack, calcsize
from Persistent import PersistentList

class KeyValueList(PersistentList):
    def __init__(self, file_object, key_format, val_format, address=None):
        self.file_object  = file_object
        self.key_format   = key_format
        self.key_size     = calcsize(key_format) 
        self.val_format   = val_format
        self.val_size     = calcsize(val_format) 
        PersistentList.__init__(self, file_object, key_format + val_format, address)

    def set(self, key, value):
        # TODO Change this to delete node and append new one
        # TODO Move StringStringList to inherit from KeyValueList
        for node in self.node_iter():
            cur_key, cur_val = self.__get_key_val__(node)
            if cur_key == key:
                node.set_value(key, value)
                break
        else:
            PersistentList.append(self, key, value)

    def get(self, key):
        for cur_key, val in self:
            if cur_key == key:
                return val

    def __get_key_val__(self, node):
        bytes = node.get_bytes()
        key   = unpack(self.key_format, bytes[:self.key_size])
        val   = unpack(self.val_format, bytes[self.key_size: self.key_size + self.val_size])
        if len(key) == 1:
            key = key[0]
        if len(val) == 1:
            val = val[0]
        return (key, val)

    def __iter__(self):
        for node in self.node_iter():
            yield self.__get_key_val__(node)
