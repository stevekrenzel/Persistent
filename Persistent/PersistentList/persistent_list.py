#!/usr/bin/python
############################################
# Released in the Public Domain, do with it
# as you please.
#
# Author: Steve Krenzel (sgk284@gmail.com)
############################################

from struct import pack, unpack, calcsize

class PersistentList:
    def __init__(self, file_object, value_format, address=None):
        self.file_object  = file_object
        self.value_format = value_format
        self.head         = None
        self.tail         = None
        if address != None and address != 0:
            self.head    = PersistentNode(self.file_object, self.value_format, address=address)
            self.tail    = None
            for node in self.node_iter():
                self.tail = node

    def append(self, *value):
        new_node = PersistentNode(self.file_object, self.value_format, value)
        if self.head == None:
            self.head = new_node
        else:
            self.tail.set_next(new_node)
        self.tail = new_node

    def node_iter(self):
        current = self.head
        while current is not None:
            yield current
            current = current.get_next()

    def __iter__(self):
        for i in self.node_iter():
            yield i.get_value()

    def __str__(self):
        return "[" + ", ".join([str(i) for i in self]) + "]"

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
            self.file_object.write(pack(self.data_format, *value))
            self.address = self.file_object.tell()
        else:
            self.address = address

    def set_value(self, *value):
        data = self.get_data() 
        data = list(value) + [data[-1]]
        self.set_data(data)

    def set_next(self, next):
        data = self.get_data() 
        data[-1] = next.address
        self.set_data(data)

    def set_data(self, data):
        self.file_object.seek(self.address - self.data_length)
        self.file_object.write(pack(self.data_format, *data))

    def get_value(self):
        value = self.get_data()[:-1]
        # If only a single value, just return the value rather than a tuple
        return value if len(value) > 1 else value[0] 

    def get_next(self):
        next = self.get_data()[-1]
        if next != 0:
            return PersistentNode(self.file_object, self.value_format, address=next)
        return None

    def get_data(self):
        self.file_object.seek(self.address - self.data_length)
        bytes = self.file_object.read(self.data_length)
        return list(unpack(self.data_format, bytes))

    def __str__(self):
        next = self.get_next()
        return "{value : %s, next : %s}"%(self.get_value(), next.address if next is not None else None)
