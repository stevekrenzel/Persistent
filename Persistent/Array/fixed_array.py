import os
from struct import pack, unpack, calcsize

class FixedArray:
    """ FixedArray creates an araray of a fixed size on disk. The array
    elements are Data objects.

    The behavior of this array is just like any standard array. It
    allocates a chunk of space, and then you specify an index to read
    into it or get something out of it. Access times are constant time.

    Bounds are also checked. Attempting to access an index that is out of
    bounds will throw an exception.

    You usually won't use this class directly, but rather it is used by
    many other containers, including Array, Hashset, and Hashmap.

    >>> from Persistent import Data, StringProperty
    >>> class User(Data):
    ...   username = StringProperty(length=25)
    ...   password = StringProperty(length=25)
    ...
    >>> a = FixedArray(User, "fixedarray_doctest.db")
    >>> a[0] = User(username="Steve", password="password")
    >>> a[1] = User(username="John")
    >>> print a[0]
    {password: password, username: Steve}
    >>> print a[1]
    {password: None, username: John}
    >>> a.close()

    >>> b = FixedArray(User, "fixedarray_doctest.db")
    >>> print b[0]
    {password: password, username: Steve}
    >>> print b[1]
    {password: None, username: John}
    >>> b.close()

    >>> obj = open("fixedarray_doctest.db", 'r+b')
    >>> c = FixedArray(User, file_object=obj, address=0)
    >>> print c[0]
    {password: password, username: Steve}
    >>> print c[1]
    {password: None, username: John}
    >>> c.close()

    >>> import os
    >>> os.remove("fixedarray_doctest.db")

    """

    def __init__(self, data, file_name=None, file_object=None, allocation=1024, address=None):
        """ Initializes a new fixed array.

        Data is the Data class for the elements of this array.

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

        The address is the starting address of the container. By default,
        and most of the time, it will be 0. Meaning that the first thing in
        this file is the container. If the address is anything other than None,
        then the allocation argument is ignored (because it implies that the
        array has already been allocated),

        """
        if file_name != None:
            if not os.path.exists(file_name):
                # Create the file if it doesn't exist
                open(file_name, 'w').close()
            elif address == None:
                # If the file exists already and no address is supplied
                address = 0
            file_object = open(file_name, 'r+b')
        # When the Data object is first initialized, it sets up certain
        # things in the class. We force the initialization here.
        data()
        self.file_object     = file_object
        self.data            = data
        self.allocation      = allocation
        self.size            = allocation * data._size
        self.address         = address

        # We allocate space at the end of the file if there is no address
        if self.address == None:
            # Seek to the end of the file and record the address
            self.file_object.seek(0, 2)
            self.address = self.file_object.tell()

            # Write how big this array is
            self.file_object.write(pack("q", self.size))

            # Allocate the space for the elements
            self._allocate_space(self.size)
        else:
            # Seek to the start of the array
            self.file_object.seek(self.address)

            # Set the size and allocation of the array
            self.size       = unpack("q", self.file_object.read(calcsize("q")))[0]
            self.allocation = self.size / self.data._size


    def _allocate_space(self, size):
        """ Allocates space for the array elements.

        Size is the number of bytes to allocate.

        >>> from cStringIO import StringIO
        >>> obj = StringIO()
        >>> from Persistent import Data, IntegerProperty
        >>> class Integer(Data):
        ...   value = IntegerProperty()
        ...
        >>> a = FixedArray(Integer, file_object=obj, allocation=10000)
        >>> obj.seek(0,2) # Seek to end of file
        >>> obj.tell()
        90008

        """
        # We write half a megabyte at a time
        block_size = 512 * 1024

        # We create a block of data filled with invalid addresses
        zeroed_block  = chr(255) * block_size

        # Write the blocks to disk
        for i in xrange(size / block_size):
            self.file_object.write(zeroed_block)

        # The last block won't likely be a full block, so we create a
        # special block for the last one.
        zeroed_block = chr(255) * (size % block_size)
        self.file_object.write(zeroed_block)

    def __setitem__(self, index, data):
        """ Sets a value in the array.

        Index is the index of the element to set.

        Data is the the data to set the element to.

        """
        self.commit(data, index)

    def __getitem__(self, index):
        """ Gets a value from the array.

        Index is the index of the element you want to retrieve.

        If all the bytes are chr(255), then that implies that no data object
        has been stored there (No valid data object will consist of all 0xFF
        bytes). In that case, we return None instead of a data object.

        """

        # Find the address of the index
        address = self._get_address(index)
        self.file_object.seek(address)

        # Read in the bytes for the data object
        bytes = self.file_object.read(self.data._size)

        # If all the bytes are chr(0), then there is no data object
        if bytes[0] == chr(255) and len(set(bytes)) == 1:
            data = None
        # Otherwise, we deserialize the bytes
        else:
            data = self.data(self, bytes)

        # Set the data object's index attribute (which can be used by commit())
        data.fixed_array_index_ = index
        return data

    def commit(self, data, index=None):
        """ Writes a data object to the array.

        If an index is supplied, the data is written at the respective index.
        If no  index is supplied, the data object is checked to see if it has
        an index property. If it does, then that is used.

        >>> from cStringIO import StringIO
        >>> obj = StringIO()
        >>> from Persistent import Data, IntegerProperty
        >>> class Integer(Data):
        ...   value = IntegerProperty()
        ...
        >>> a = FixedArray(Integer, file_object=obj)
        >>> i = Integer(value=9)
        >>> a.commit(i, 5)
        >>> print a[5]
        {value: 9}

        >>> # Here we show that the fixed_array_index attribute works
        >>> b = a[5]
        >>> b.value = 3
        >>> a.commit(b)
        >>> print a[5]
        {value: 3}

        """
        if index == None:
            if hasattr(data, 'fixed_array_index_'):
                index = data.fixed_array_index_
            else:
                raise Exception("Data has no associated index")
        address = self._get_address(index)
        self.file_object.seek(address)
        self.file_object.write(data.unload())

    def _get_address(self, index):
        """ Given an index, will return the address of the element in the
        file.

        If the index is out of bounds, an exception is thrown.

        >>> from cStringIO import StringIO
        >>> obj = StringIO()
        >>> from Persistent import Data, IntegerProperty
        >>> class Integer(Data):
        ...   value = IntegerProperty()
        ...
        >>> a = FixedArray(Integer, file_object=obj)
        >>> a._get_address(0)
        8
        >>> a._get_address(100)
        908
        >>> a._get_address(1023)
        9215
        >>> a._get_address(1024)
        Traceback (most recent call last):
        Exception: Index is out of bounds

        """

        # We add calcsize('q') because the fisrt few bytes are the length of
        # the array
        if index >= self.allocation:
            raise Exception("Index is out of bounds")
        return self.address + calcsize("q") + (index * self.data._size)

    def close(self):
        """ Closes the array's file object. """

        self.file_object.close()
