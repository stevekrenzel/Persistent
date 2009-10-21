###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from Persistent import Data, FixedArray
from struct import pack, unpack, calcsize
from time import time
from random import randint
from hashlib import md5

class FixedSet(FixedArray):

    def __init__(self, format, file_object, allocation=1024, probe_size=120, address=None):
        FixedArray.__init__(self, format, file_object, allocation, address)
        self.probe_size = min(allocation, probe_size)
        self.empty_cell = chr(255) * self.format_size
        self.range      = (self.size/self.format_size) - self.probe_size + 1
        self.long_sz    = calcsize("q")
        # TODO Write all construction information to disk

    def set(self, data):
        address = self.__get_address__(data.bytes)
        self.file_object.seek(address)
        bytes = self.file_object.read(self.format_size * self.probe_size)
        for d in (data.bytes, self.empty_cell):
            index = self.__find_by_bytes__(d, bytes)
            if index != None:
                self.file_object.seek(address + index)
                self.file_object.write(data.bytes)
                return True
        return False

    def get(self, data):
        address = self.__get_address__(data.bytes)
        self.file_object.seek(address)
        bytes = self.file_object.read(self.format_size * self.probe_size)
        index = self.__find_by_bytes__(data.bytes, bytes)
        if index != None:
            raw = bytes[index : index + self.format_size]
            return Data(self.format, self.file_object, address + index, raw)
        return None

    def __find_by_bytes__(self, data_bytes, lookup_bytes):
        # NOTE: For hashmap/keyvalue only use key bytes
        if data_bytes not in lookup_bytes:
            return None
        index = lookup_bytes.find(data_bytes)
        while index != -1:
            if index % self.format_size == 0:
                return index
            index = lookup_bytes.find(data.bytes, index + 1)
        return None

    def __contains__(self, data):
        return self.get(data) != None

    def __get_address__(self, bytes):
        slot    = int(md5(bytes).hexdigest(), 16) % self.range
        offset  = slot * self.format_size
        return self.address + self.long_sz + offset

if __name__ == "__main__":
    import os

    filename = "set_test.db"
    rands    = set([randint(0, 50000000) for i in xrange(20000)])
    rlen     = len(rands)*5
    format    = "I:age, 20p:name"
    d         = Data(format)
    d["age"]  = 9
    d["name"] = "Steve"
    print rlen

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()
    db    = open(filename, "r+b")

    seta  = FixedSet(format, db, rlen, 20)
    t     = time()
    c     = 0
    for i, e in enumerate(rands):
        d["age"] = e
        if seta.set(d) != True:
            break
        c += 1
    u = time() - t
    print c/float(rlen), c/u, u

    db.close()
    os.remove(filename)
