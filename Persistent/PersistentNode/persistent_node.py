############################################
# Released in the Public Domain, do with it
# as you please.
#
# Author: Steve Krenzel (sgk284@gmail.com)
############################################

from struct import pack, unpack, calcsize

class PersistentNode:
    def __init__(self, file_object, value_format, value = None, next = None, address=None):
        self.file_object  = file_object
        self.value_format = value_format
        self.value_length = calcsize(self.value_format)
        self.data_format  = self.value_format + "I" # Add pointer 
        self.data_length  = calcsize(self.data_format)
        if address == None or address == 0:
            self.file_object.seek(0, 2)
            value = [0]*self.value_length if value is None else list(value)
            value.append(0 if next is None else next.address)
            self.bytes = pack(self.data_format, *value)
            self.file_object.write(self.bytes)
            self.address = self.file_object.tell()
        else:
            self.address = address
            self.file_object.seek(self.address - self.data_length)
            self.bytes = self.file_object.read(self.data_length)

    def set_value(self, *value):
        data = self.get_data() 
        data = list(value) + [data[-1]]
        self.set_data(data)

    def set_next(self, next):
        data = self.get_data() 
        data[-1] = next.address if next is not None else 0
        self.set_data(data)

    def set_next_address(self, next_address):
        data = self.get_data() 
        data[-1] = next.address if next is not None else 0
        self.set_data(data)

    def set_data(self, data):
        self.file_object.seek(self.address - self.data_length)
        self.bytes = pack(self.data_format, *data)
        self.file_object.write(self.bytes)

    def get_value(self):
        value = self.get_data()[:-1]
        # If only a single value, just return the value rather than a tuple
        return value if len(value) > 1 else value[0] 

    def get_next_address(self):
        return self.get_data()[-1]

    def get_next(self):
        next = self.get_data()[-1]
        if next != 0:
            return PersistentNode(self.file_object, self.value_format, address=next)
        return None

    def get_data(self):
        return list(unpack(self.data_format, self.get_bytes()))

    def get_bytes(self):
        return self.bytes

    def __str__(self):
        next = self.get_next()
        return "{value : %s, next : %s}"%(self.get_value(), next.address if next is not None else None)