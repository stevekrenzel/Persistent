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
import md5

class FixedSet(FixedArray):

    def __init__(self, format, file_object, allocation=1024, probe_size=20, address=None):
        FixedArray.__init__(self, format, file_object, allocation, address)
        self.probe_size = min(allocation, probe_size)
        self.empty_cell = chr(255) * self.format_size
        self.range      = (self.size/self.format_size) - self.probe_size
        # TODO Write all construction information to disk

    def set(self, data):
        address = self.__get_address__(data)
        self.file_object.seek(address)
        length  = self.format_size
        bytes   = self.file_object.read(self.format_size * self.probe_size)
        for i in range(self.probe_size):
            raw             = bytes[i * length : (i + 1) * length]
            current_address = address + (i * self.format_size)
            current         = Data(self.format, self.file_object, current_address, raw)
            if raw == self.empty_cell or data == current:
                current.set(*data.value)
                return True
        return False

    def get(self, data):
        address = self.__get_address__(data)
        self.file_object.seek(address)
        length  = self.format_size
        bytes   = self.file_object.read(self.format_size * self.probe_size)
        for i in range(self.probe_size):
            raw             = bytes[i * length : (i + 1) * length]
            current_address = address + (i * self.format_size)
            current         = Data(self.format, self.file_object, current_address, raw)
            if raw == self.empty_cell:
                return None
            if data == current:
                return current

    def __contains__(self, data):
        return self.get(data) != None

    def __get_address__(self, object):
        md5_int = int(md5.new(str(object)).hexdigest(), 16)
        slot   =  md5_int % (self.range + 1)
        offset = slot * self.format_size
        return self.address + calcsize("q") + offset

if __name__ == "__main__":
    import os

    filename = "set_test.db"
    rands    = set([randint(0, 50000000) for i in xrange(1000000)])
    rlen     = len(rands)
    format    = "I:age, 20p:name"
    d         = Data(format)
    d["age"]  = 9
    d["name"] = "Steve"
    print rlen
    for prs in xrange(0, 1500, 10):
        # Create the file if it doesn't exist
        if not os.path.exists(filename):
            open(filename, 'w').close()
        db    = open(filename, "r+b")
        seta  = FixedSet(format, db, rlen, prs)
        t     = time()
        c     = 0
        for i, e in enumerate(rands):
            d["age"] = e
            if seta.set(d) != True:
                break
            c += 1
        u = time() - t
        print prs, c/float(rlen), c/u
        db.close()
        os.remove(filename)
