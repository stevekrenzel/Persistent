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
    """The PersistentList is a linked list composed of PersistentNodes. It's
    primary role is to track the head of the list, as well as handle standard
    list operations.
    TODO: Store tail and length in file

    """

    def __init__(self, file_object, value_format, address=None):
        """Initiates the persistent list. I hate useless comments like this."""

        self.file_object  = file_object
        self.value_format = value_format
        self.head         = None
        self.tail         = None

        # We do lazy loading of the tailx because to find it the first time we
        # need to iterate through all of the nodes. We don't actually need to
        # know the tail until we append something, so as we iterate through the
        # list we keep setting the tail. In long lists this will save us some
        # seeks when we actually need to get the tail.
        #
        # For example, we have a list of 100 nodes. We've iterated through
        # 75 of them. 'self.tail' will be set to the 75th node, but since
        # 'self.tail_set' isn't True, we know that 'self.tail' isn't the actual
        # tail. When it comes time to find the actual tail though, we can start
        # at the 75th node because we know it's at least after that point.
        self.tail_set = False

        # If an address is provided, we load the head node from disk
        if address != None and address != 0:
            self.head = PersistentNode(self.file_object, self.value_format, address=address)

    def __set_tail__(self):
        """Iterates from the current furthest known node to the end of the
        list and stores the tail.

        """
        for node in self.node_iter(self.tail):
            self.tail = node
        self.tail_set = True

    def append(self, *value, **alt):
        """Appends a new node to the end of the list. Also, if the keyword
        argument 'post_data' is set, that post data will be written on disk
        directly after the node.

        """
        # If the tail node hasn't been set, set it.
        if not self.tail_set:
            self.__set_tail__()

        # Create the new node. This also writes it to disk.
        new_node = PersistentNode(self.file_object, self.value_format, value)

        # If there is any post_data specified, we'll write that to disk too.
        if "post_data" in alt:
            self.file_object.write(alt["post_data"])

        # If this is the first node in the list, set the head node to it
        if self.head == None:
            self.head = new_node
        # Otherwise, add it after the tail
        else:
            self.tail.set_next(new_node)

        # Update the tail, which is now the new node
        self.tail = new_node

    def find(self, *value):
        """Finds and returns the first node in the list that matches the value
        given in the argument.

        """
        # If the value is of length one, we just use the value (by taking it out
        # of the list). This is for compatibility with the way PersistentNode
        # returns values.
        if len(value) == 1:
            value = value[0]

        for node, node_val in self.items():
            if node_val == value:
                return node

    def delete(self, *value):
        """Works like find(), but deletes the node as well."""

        # If only one value is passed, we don't use the tuple.
        # If multiple values are passed, we convert the tuple
        # to a list for compatibility with the PersistentNode
        # get_value() rerturn value.
        value = value[0] if len(value) == 1 else list(value)

        # Tracks the previous node because this is a singly linked list and we
        # need it to remove the current node.
        prev_node = None
        
        # We iterate through the list and break out of the loop when we find
        # the node we want to delete.
        for node, node_val in self.items():
            if node_val == value:
                break
            prev_node = node

        next = node.get_next()

        # If no previous node was set, that means this is the head
        if prev_node is None:
            self.head = next 
        else:
            prev_node.set_next(next)

        # If there was no next node, that means this is the tail
        if next == None:
            self.tail     = prev_node
            self.tail_set = self.tail is not None

    def node_iter(self, start = None):
        """Iterates through all the nodes in the list. By default, it starts
        with the head of the list, but if you pass in a start node, it'll
        start iterating there.

        """
        current = start or self.head
        while current is not None:
            yield current

            # We keep updating the last known node to save us from reiterating
            # over these same nodes later when we need to find the tail
            if not self.tail_set:
                self.tail = current
            current = current.get_next()
        
        # If we make it out of the loop, we've iterated through all nodes and
        # thus the tail has been set.
        self.tail_set = True

    def items(self):    
        """Iterates through the list, but returns tuples of the (node, value)
        for convenience. 

        """
        for i in self.node_iter():
            yield(i, i.get_value())

    def __iter__(self):
        """Iterates through each value in the list and returns it.""" 
        for node, value in self.items():
            yield value

    def __str__(self):
        """Returns a string representation of the list similar to the python
        representation of lists."""
        return "[" + ", ".join([str(i) for i in self]) + "]"
