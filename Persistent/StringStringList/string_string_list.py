from struct import pack, unpack, calcsize
from Persistent import KeyValueList
from Persistent import PersistentList

class StringStringList(PersistentList):
    # Warning: Operations are O(N)
    def __init__(self, file_object, address=None):
        PersistentList.__init__(self, file_object, "iII", address)

    def set(self, key, value):
        key_hash = hash(key)
        key_len  = len(key)
        val_len  = len(value)
        self.delete(key_hash, key_len)# TODO Delete by key, not hash and len
        PersistentList.append(self, key_hash, key_len, val_len, post_data = key + value)
       
    def get(self, key):
        new_key_hash = hash(key)
        new_key_len  = len(key)
        node = self.find(new_key_hash, new_key_len)
        if node is not None:
            cur_key_hash, cur_key_len, cur_val_len = node.get_value()
            cur_key, cur_val = self.__get_key_val__(cur_key_len, cur_val_len)
            if cur_key == key:
                return cur_val

    def node_value_iter(self):
        for i in self.node_iter():
            yield(i, tuple(i.get_value()[:-1]))

    def __get_key_val__(self, key_len, val_len):
        data = self.file_object.read(key_len + val_len)
        return [data[:key_len], data[key_len:]]

    def __add_key_val__(self, key, val):
        self.file_object.seek(0, 2)
        address = self.file_object.tell()
        self.file_object.write(key+val)
        return address
