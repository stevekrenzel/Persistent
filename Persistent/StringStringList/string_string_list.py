from struct import pack, unpack, calcsize
from Persistent import KeyValueList
from Persistent import PersistentList

class StringStringList(PersistentList):
    # Warning: Operations are O(N)
    def __init__(self, file_object, address=None):
        PersistentList.__init__(self, file_object, "IiII", address)

    def set(self, key, value):
        new_address  = self.__add_key_val__(key, value)
        new_key_len  = len(key)
        new_key_hash = hash(key)
        for address, cur_key_hash, cur_key_len, cur_val_len in self:
            if cur_key_hash == new_key_hash and cur_key_len == new_key_len:
                cur_key, cur_val = self.__get_key_val__(address, cur_key_len, cur_val_len)
                if cur_key == key:
                    node.set_value(new_address, new_key_hash, new_key_len, len(value))
                    break
        else:
            PersistentList.append(self, new_address, hash(key), len(key), len(value))

    def get(self, key):
        new_key_len  = len(key)
        new_key_hash = hash(key)
        for address, cur_key_hash, cur_key_len, cur_val_len in self:
            if cur_key_hash == new_key_hash and cur_key_len == new_key_len:
                cur_key, cur_val = self.__get_key_val__(address, cur_key_len, cur_val_len)
                if cur_key == key:
                    return cur_val

    def __get_key_val__(self, address, key_len, val_len):
        self.file_object.seek(address)
        data = self.file_object.read(key_len + val_len)
        return [data[:key_len], data[key_len:]]

    def __add_key_val__(self, key, val):
        self.file_object.seek(0, 2)
        address = self.file_object.tell()
        self.file_object.write(key+val)
        return address
