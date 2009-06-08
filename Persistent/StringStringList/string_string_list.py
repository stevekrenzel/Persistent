###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from struct import pack, unpack, calcsize
from Persistent import KeyValueList
from Persistent import PersistentList

class StringStringList(PersistentList):
    # Warning: Operations are O(N)
    def __init__(self, file_object, address=None):
        PersistentList.__init__(self, file_object, "iII", address)

    def set(self, key, value):
        key_hash, key_len, val_len = hash(key), len(key), len(value)
        self.delete(key_hash, key_len)# TODO Delete by key, not hash and len
        PersistentList.append(self, key_hash, key_len, val_len, post_data = key + value)
       
    def get(self, key):
        new_key_hash = hash(key)
        new_key_len  = len(key)
        node = self.find(new_key_hash, new_key_len)
        if node is not None:
            cur_key_hash, cur_key_len, cur_val_len = node.get_value()
            self.file_object.seek(node.address)
            data = self.file_object.read(cur_key_len + cur_val_len)
            cur_key, cur_val = data[:cur_key_len], data[cur_key_len:]
            if cur_key == key:
                return cur_val

    def items(self):
        for node, value in PersistentList.items(self):
            yield(node, value[:-1])

    def __add_key_val__(self, key, val):
        self.file_object.seek(0, 2)
        address = self.file_object.tell()
        self.file_object.write(key+val)
        return address
