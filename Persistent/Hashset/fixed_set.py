###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize
from hashlib import md5
from Persistent.Array.fixed_array import FixedArray

class FixedSet(FixedArray):

    def __init__(self, data, file_name, file_object=None, allocation=1024, probe_size=75, address=None):
        FixedArray.__init__(self, data, file_name, file_object, allocation, address)
        allocation      = self.size/self.data._size
        self.probe_size = min(allocation, probe_size)
        self.empty_cell = chr(255) * self.data._size
        self.range      = allocation - self.probe_size + 1
        self.long_sz    = calcsize("q")
        # TODO Write all construction information to disk

    def set(self, data):
        bytes        = data.unload_key() if data._keys else data.unload()
        address, raw = self.__find_bytes__(bytes)
        index        = self.__find_by_bytes__(bytes, raw)
        if index != None:
            # We only write data if this has keys because otherwise
            # we've already confirmed that these bits exist on disk
            if data._keys:
                self.__commit__(data, address=address + index)
            return True
        index = self.__find_by_bytes__(self.empty_cell, raw)
        if index != None:
            self.__commit__(data, address=address + index)
            return True
        return False

    def get(self, data):
        bytes = data.unload_key() if data._keys else data.unload()
        address, raw = self.__find_bytes__(bytes)
        index = self.__find_by_bytes__(bytes, raw)
        if index != None:
            return self.data(self, raw[index : index + self.data._size])
        return None

    def __commit__(self, data, bytes=None, address=None):
        if address == None:
            return self.set(data)
        if bytes == None:
            bytes = data.unload()
        self.file_object.seek(address)
        self.file_object.write(bytes)

    def __find_bytes__(self, bytes):
        address = self.__get_address__(bytes)
        self.file_object.seek(address)
        return (address, self.file_object.read(self.data._size * self.probe_size))

    def __find_by_bytes__(self, data_bytes, lookup_bytes):
        if data_bytes not in lookup_bytes:
            return None
        index = lookup_bytes.find(data_bytes)
        while index != -1:
            if index % self.data._size == 0:
                return index
            index = lookup_bytes.find(data_bytes, index + 1)
        return None

    def __get_address__(self, bytes):
        slot    = int(md5(bytes).hexdigest(), 16) % self.range
        offset  = slot * self.data._size
        return self.address + self.long_sz + offset

    def __contains__(self, data):
        return self.get(data) != None
