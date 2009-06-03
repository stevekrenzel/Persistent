from Persistent import PersistentMap, StringStringList

class StringStringMap(PersistentMap):
    def __init__(self, file_object, map_size, address=None):
        PersistentMap.__init__(self, file_object, None, None, map_size, address)

    #TODO Append string data right after node data and avoid the extra seek and read
    # address len len ..... data data
    # to
    # len len data data
    def __make_list__(self, file_object, key_format, value_format, address=None):
       return StringStringList(file_object, address) 
