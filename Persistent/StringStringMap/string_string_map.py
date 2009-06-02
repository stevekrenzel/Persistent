from Persistent import PersistentMap, StringStringList

class StringStringMap(PersistentMap):
    def __init__(self, file_object, map_size, address=None):
        PersistentMap.__init__(self, file_object, None, None, map_size, address)

    def __make_list__(self, file_object, key_format, value_format, address=None):
       return StringStringList(file_object, address) 
