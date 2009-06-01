from Persistent import PersistentList

class IntegerList(PersistentList):
    def __init__(self, file_object, number_of_ints=1, address=0):
        PersistentList.__init__(self, file_object, "I"*number_of_ints,
                address=address)
