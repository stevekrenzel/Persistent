from struct import calcsize
from hashlib import md5
from Persistent.Array.fixed_array import FixedArray

class FixedSet(FixedArray):
    """ FixedSet is fixed size set on disk. The set elements are Data objects.

    The behaviour of this FixedSet is similar to any typical set. It's an
    unordered container of items, where each item is unique.

    A chunk of space is allocated for elements. You then add elements as
    necessary. The position that the elements are saved to is chosen according
    to the hash of the data being stored. Each element will only occur once,
    there will be no duplicates. That is, adding the same element twice will
    be a noop.

    You usually shouldn't use this class directly. While we allocate a certain
    amount of space, the actual number of elements that can be added will be
    random due to collision behavior. Instead, use Hashset, which grows as more
    space is needed.

    As far as how the hashset is implemented, it is pretty straight forward.
    By default we allocate space for 1024 elements. When we add a new element
    to the set, we hash it's contents to calculate the address that the element
    will be stored at. We then seek to that address, and probe the following 75
    elements for a spot that hasn't been set yet, or already contains our
    element. When this spot is found, we write the data to disk. We do a
    similar process for getting elements as well.

    >>> from Persistent import Data, StringProperty
    >>> class User(Data):
    ...   username = StringProperty(length=25)
    ...   password = StringProperty(length=25)
    ...
    >>> s = FixedSet(User, "fixedset_doctest.db")
    >>> for i in xrange(100):
    ...   nil = s.set(User(username=str(i), password=str(i)))
    >>> for i in xrange(100):
    ...   u = s.get(User(username=str(i), password=str(i)))
    ...   if u.username != str(i) or u.password != str(i):
    ...     print "Oops, user values aren't what was expected."
    >>> import os
    >>> os.remove("fixedset_doctest.db")

    """

    def __init__(self, data, file_name, file_object=None, allocation=1024,
            probe_size=75, address=None):
        """ Initializes a new fixed set.

        Data is the Data class for the elements of the set.

        Either a file_name or a file_object must be specified. If you specify
        a name, we check for the existence of the file. If the file exists,
        we simply open it, otherwise we create it and then open it. If a file
        object is specified, we just use that object.

        If a file_name is specified for a file that already exists, we assume
        that file already contains the container we're trying to create, so
        instead of initializing space for a new container, we simply use the
        container that already exists. This lets you easily save an array or
        other container to disk, and then reopen it later.

        The allocation variable specifies how many elements we should allocate
        space for. If we allocate space for 1,000 elements and each element
        takes 10 bytes of space, then we allocate 10,000 bytes for this
        container.

        The probe size is the number of elements we probe when setting
        or getting an element. Making this number smaller results in better
        performance, but more space is wasted. Making this number larger
        results in more effcient use of space, but decreases performance.

        The address is the starting address of the container. By default,
        and most of the time, it will be 0. Meaning that the first thing in
        this file is the container. If the address is anything other than None,
        then the allocation argument is ignored (because it implies that the
        array has already been allocated),

        """
        FixedArray.__init__(self, data, file_name, file_object, allocation,
            address)
        allocation      = self.size/self.data._size
        self.probe_size = min(allocation, probe_size)
        self.empty_cell = chr(255) * self.data._size
        self.range      = allocation - self.probe_size + 1
        # TODO Write all construction information to disk

    def _get_bytes_address_raw(self, data):
        """ This is a helper function that consolidates some of the common
        logic in set() and get().

        It determines what bytes from the data object are of interest. If
        we're dealing with a map, we only care about the bytes for the keys,
        but if we're dealing with a set, we care about all of the bytes for the
        data.

        It also calculates what address in the file we are interested in for
        the given bytes. This is determined by the hash of the bytes.

        Finally, it reads in the raw bytes from the FixedSet that we want to
        probe.

        It then returns that data bytes, file address, and raw probe bytes.

        If you can think of a better name for this function, I'm all ears.

        >>> from Persistent import Data, StringProperty
        >>> class User(Data):
        ...   username = StringProperty(length=5, key=True)
        ...   password = StringProperty(length=8)
        ...
        >>> s = FixedSet(User, "fixedset_doctest.db")

        >>> # First we try this with a normal data object
        >>> u = User(username="Steve", password="password")
        >>> s.set(u)
        True
        >>> bytes, address, raw = s._get_bytes_address_raw(u)
        >>> bytes
        '\\x01\\x05\\x00\\x00\\x00Steve\\x01\\x08\\x00\\x00\\x00password\\xba\\xa8\\xf4/'
        >>> address
        3491L
        >>> raw == bytes + '\\xff' * 1998
        True

        >>> # Now we try it with a data object for a map
        >>> u._is_map = True
        >>> s.set(u)
        True
        >>> key_bytes, address, raw = s._get_bytes_address_raw(u)
        >>> key_bytes
        '\\x01\\x05\\x00\\x00\\x00Steve'
        >>> address
        24794L
        >>> raw == bytes + '\\xff' * 1998
        True

        >>> import os
        >>> os.remove("fixedset_doctest.db")

        """
        if getattr(data, '_is_map', False):
            bytes = data.unload_key()
        else:
            bytes = data.unload()
        address, raw = self._get_address_and_probe_bytes(bytes)
        return bytes, address, raw

    def _get_address_and_probe_bytes(self, bytes):
        """ Given a series of bytes, this will return the address associated
        with these bytes, as well as the bytes that should be probed at this
        given adddress.

        """
        address = self._get_address(bytes)
        self.file_object.seek(address)
        return (address,
            self.file_object.read(self.data._size * self.probe_size))

    def _get_address(self, bytes):
        """ Given a series of bytes, we hash them and mod them according to
        the range of the given fixed set. From this, we return the address
        that these bytes should be present at.

        """
        # First we calculate what "slot" these bytes fall in. In an array,
        # this would be the index of the element.
        slot = int(md5(bytes).hexdigest(), 16) % self.range

        # Once we have the "slot", we convert that to the number of bytes
        # from the start of the set.
        offset = slot * self.data._size

        # Finally, once we have the offset, we prepend long_sz to account
        # for the first few bytes which represent the size of the underlying
        # array. We then add this to the address of the set to determine the
        # address in the file at which these bytes are present.
        return self.address + self.long_sz + offset

    def set(self, data):
        """ Adds an element to the set. """
        # We get the data bytes, the address of this element and the raw bytes
        # to probe
        bytes, address, raw = self._get_bytes_address_raw(data)

        # We search for "bytes" to see if this object already exists in the
        # set. If it isn't found, then we just find the first empty cell and
        # store the object there.
        for b in [bytes, self.empty_cell]:
            index = self._find_by_bytes(b, raw)
            if index != None:
                self.file_object.seek(address + index)
                self.file_object.write(data.unload())
                return True
        return False

    def get(self, data):
        """ Gets an element from the set. """
        # We get the data bytes, the address of this element and the raw bytes
        # to probe
        bytes, address, raw = self._get_bytes_address_raw(data)

        # If we find the bytes in our probe, we return a new data object
        # created from those bytes.
        index = self._find_by_bytes(bytes, raw)
        if index != None:
            return self.data(self, raw[index : index + self.data._size])
        return None

    def _find_by_bytes(self, data_bytes, lookup_bytes):
        """ Returns the first occurence of data_bytes in lookup_bytes.

        This ensures that the returned index is on the boundary of a data
        object.

        Simply returning lokoup_bytes.find(data_bytes) might return an index
        that falls in the middle of an element depending upon the bytes you're
        searching for.

        """
        index = lookup_bytes.find(data_bytes)
        while index != -1:
            if index % self.data._size == 0:
                return index
            index = lookup_bytes.find(data_bytes, index + 1)
        return None

    def __contains__(self, data):
        """ Returns True is the data object is present in the set. """
        return self.get(data) != None
