from Persistent import PersistentMap

class IntegerIntegerMap(PersistentMap):
    def __init__(self, file_object, map_size, address=None, key_ints=1, val_ints=1):
        PersistentMap.__init__(self, file_object, "I"*key_ints, "I"*val_ints, map_size, address=address)
