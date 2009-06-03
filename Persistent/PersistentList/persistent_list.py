###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################
from struct import pack, unpack, calcsize
from Persistent import PersistentNode

class PersistentList:
    # TODO Store tail
    def __init__(self, file_object, value_format, address=None):
        self.file_object  = file_object
        self.value_format = value_format
        self.head         = None
        self.tail         = None
        self.tail_set     = False
        if address != None and address != 0:
            self.head     = PersistentNode(self.file_object, self.value_format, address=address)
            self.tail     = None

    def __set_tail__(self):
        for node in self.node_iter(self.tail):
            self.tail = node
        self.tail_set = True

    def append(self, *value, **alt):
        if not self.tail_set:
            self.__set_tail__()
        new_node = PersistentNode(self.file_object, self.value_format, value)
        if "post_data" in alt:
            self.file_object.write(alt["post_data"])
        if self.head == None:
            self.head = new_node
        else:
            self.tail.set_next(new_node)
        self.tail = new_node

    def find(self, *value):
        if len(value) == 1:
            value = value[0]
        for node, node_val in self.node_value_iter():
            #print node_val, value
            if node_val == value:
                return node
                break

    def delete(self, *value):
        if len(value) == 1:
            value = value[0]
        prev_node = None
        for node, node_val in self.node_value_iter():
            if node_val == value:
                if prev_node is not None:
                    new_next = node.get_next()
                    prev_node.set_next(new_next)
                    if new_next == None:
                        self.tail = new_next
                        self.tail_set = True
                else:
                    self.head = node.get_next()
                    if self.head == None:
                        self.tail = None
                        self.tail_set = True
                break
            prev_node = node

    def node_iter(self, current = None):
        current = current or self.head
        while current is not None:
            yield current
            # Set the tail as we go along
            if not self.tail_set:
                self.tail = current
            current = current.get_next()
        self.tail_set = True

    def node_value_iter(self):    
        for i in self.node_iter():
            yield(i, i.get_value())

    def __iter__(self):
        for i in self.node_iter():
            yield i.get_value()

    def __str__(self):
        return "[" + ", ".join([str(i) for i in self]) + "]"
