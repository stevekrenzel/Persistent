###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from Persistent import Data
from Persistent.Hashset.fixed_set import FixedSet

class FixedMap(FixedSet):

    def __init__(self, key_format, val_format, file_object, allocation=1024, probe_size=120, address=None):
        self.key         = Data(key_format)
        self.key_format  = key_format
        self.val         = Data(val_format)
        self.val_format  = val_format
        format           = "%dc:raw"% (self.key.size + self.val.size)
        FixedSet.__init__(self, format, file_object, allocation, probe_size, address)

    def set(self, key, val):
        address, bytes = self.__find_bytes__(key)
        for d in (key.bytes, self.empty_cell):
            index = self.__find_by_bytes__(d, bytes)
            if index != None:
                self.file_object.seek(address + index)
                self.file_object.write(key.bytes + val.bytes)
                return True
        return False

    def get(self, key):
        address, bytes = self.__find_bytes__(key)
        index = self.__find_by_bytes__(key.bytes, bytes)
        if index != None:
            raw = bytes[index + key.size: index + key.size + self.val.size]
            return Data(self.val_format, self.file_object, address + key.size + index, raw)
        return None

if __name__ == "__main__":
    main()

def main():
    import os
    from time import time
    from random import randint, seed

    seed(4)
    filename = "map_test.db"
    rands    = list(set([randint(0, 50000000) for i in xrange(160000)]))
    rlen     = len(rands)*5
    format   = "I:age, 20p:name"
    k        = Data("I:age")
    v        = Data("20p:name")

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()
    db    = open(filename, "r+b")
    mapa  = FixedMap("I:age", "20p:name", db, rlen)

    t     = time()
    m     = 0
    for i, e in enumerate(rands):
        k["age"]  = e
        v["name"] = str(i)
        if mapa.set(k, v) != True:
            m = i
            break
    m = m if m != 0 else len(rands)
    print m/(time() - t)

    t     = time()
    for i in xrange(m - 1):
        k["age"]  = rands[i]
        v["name"] = str(i)
        ret       = mapa.get(k)
        if ret != v:
            print "CRAP :", k, v
            break
    print m/(time() - t)

    db.close()
    os.remove(filename)
