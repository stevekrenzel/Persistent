from math import log
from Persistent.Array.fixed_array import FixedArray
from Persistent import DynamicCollection

class Array(DynamicCollection):
    """ Array class is a dynamic array that grows as more elements are added.
    The array elements are Data objects.

    The behavior of this array is just like any standard array. It
    allocates a chunk of space, and then you specify an index to read
    into it or get something out of it. Access times are constant time.

    When you access an element that is outside of the currently allocated
    space, new space will be allocated. This applies to both gets and sets.

    This is kind of dangerous, but a design decision that I feel is okay. Just
    don't access element 1,000,000,000,000 by accident, or you'll create a
    pretty huge array.

    Because of this behvaior, a get or set should never fail for a given index,
    unless you run out of disk space.

    The implementation details of this array are different than for most
    dynamic arrays. In a typical dynamic array, a certain amount of space
    is allocated. When that space is full, we allocate twice as much space,
    copy over the original data into the new space, then delete the old space.

    For example, we would allocate enough space for 5 elements:

    _ _ _ _ _

    And then add data:

    40 52 13 95 37

    But now we want to add a sixth value, so we allocate space for 10 elements:

    _ _ _ _ _ _ _ _ _ _

    Copy over the old data:

    40 52 13 95 37 _ _ _ _ _

    Ignore the old data, and add our sixth element into the new space:

    40 52 13 95 37 21 _ _ _ _

    This has some nice characteristics, such as enforcing constant time
    indexing, as well as having nice cache behaviors.

    We, however, don't implement our dynamic array like this. Hard drives
    are slow and copying over gigabytes of data everytime we want to resize
    the array seems silly if we don't have to do it. Furthermore, we're then
    left with the old allocated space, that I suppose we could reuse... but
    then you get into fragmentation and other nonsense that I'd like to not
    worry about.

    Instead, we track multiple independent fixed sized arrays. Here is an
    example:

    We allocate space for 5 elements:
    _ _ _ _ _

    And we add data:

    40 52 13 95 37

    But now we want to add a sixth value. We allocate space for a new array
    that can hold 10 elements, but we don't forget about our old array that
    can only hold 5:

    Array 1: 40 52 13 95 37
    Array 2: _  _  _  _  _  _  _  _  _  _

    Now we add our sixth element, which happens to be the first element of the
    second array:

    Array 1: 40 52 13 95 37
    Array 2: 21 _  _  _  _  _  _  _  _  _

    When we fill up array 2, we simply add array 3 and so on.

    This has all of the same nice characteristics of the other dynamic array
    implementation, such as constant access times and nice cache behaviour,
    but when we resize our array we don't have to copy *any* data. This
    effectively gives us constant time resizes. We also no longer have to
    worry about freeing old space and fragmentation, etc...

    Calculating where a particular index is does have some more overhead,
    but since we're working off of disk, this overhead pales in comparison
    to the disk access times.

    >>> from Persistent import Data, IntegerProperty
    >>> class Integer(Data):
    ...   value = IntegerProperty()
    ...
    >>> a = Array(Integer, "array_doctest.db")
    >>> for i in xrange(10000):
    ...   a[i] = Integer(value=i)
    >>> [False for i in xrange(10000) if a[i].value != i]
    []

    >>> import os
    >>> os.remove("array_doctest.db")

    """

    def __init__(self, data, file_name=None, file_object=None, address=None):
        """ Initializes a new array.

        Data is the class for the elements that will be stored in this array

        File_name is the name of the file that contains, or will contain,
        the array. This is an optional parameter, but must be specified
        if a file_object isn't specified.

        File_object is the file object that contains, or will contain,
        the array. This is an optional parameter, but must be specified
        if a file_name isn't specified.

        Address is the address in the file that the array starts at. If
        no address is supplied, space for a new array is allocated at the
        end of the file.

        """
        # Data objects have certain varibles, such as the size of the object,
        # initialized the first time the constructoris called. Here we force
        # these variables to be intiialized.
        data()
        self.data = data
        DynamicCollection.__init__(self, file_name, file_object, address)

    def _create_collection(self, address=None):
        """ This is called when the previous array has become full and we need
        to add a new one.

        """
        allocation = (2**len(self.collections)) * self.initial_allocation
        return FixedArray(self.data, None, self.file_object, allocation, address)

    def _get_array_index(self, index):
        """ Since our array is really an array of fixed size arrays, this
        function tells us which fixed array our index is in.

        >>> from Persistent import Data, IntegerProperty
        >>> class Integer(Data):
        ...   value = IntegerProperty()
        ...
        >>> a = Array(Integer, "array_doctest.db")
        >>> a._get_array_index(0)
        0
        >>> a._get_array_index(1023)
        0
        >>> a._get_array_index(1024)
        1
        >>> a._get_array_index(10000)
        3

        >>> import os
        >>> os.remove("array_doctest.db")

        """
        block = (index / self.initial_allocation) + 1
        return int(log(block, 2))

    def _get_relative_index(self, index, array_index):
        """ Whereas _get_array_index tells us which fixed array our index is
        in, this tells us where within the fixed_array this particular index
        is.

        >>> from Persistent import Data, IntegerProperty
        >>> class Integer(Data):
        ...   value = IntegerProperty()
        ...
        >>> a = Array(Integer, "array_doctest.db")
        >>> a._get_relative_index(0, a._get_array_index(0))
        0
        >>> a._get_relative_index(1023, a._get_array_index(1023))
        1023
        >>> a._get_relative_index(1024, a._get_array_index(1024))
        0
        >>> a._get_relative_index(10000, a._get_array_index(10000))
        2832

        >>> import os
        >>> os.remove("array_doctest.db")

        """
        if array_index > 0:
            return index - self.initial_allocation*((2**array_index)-1)
        return index

    def __setitem__(self, index, data):
        """ Sets the index of this array equal to the data specified.

        If the index specified is outside of the currently allocated space for
        the array, additional space will be allocated.

        """
        #TODO For data objects with only one property, allow setting like:
        # a[5] = "Steve"
        array_index    = self._get_array_index(index)
        relative_index = self._get_relative_index(index, array_index)
        if array_index < len(self.collections):
            self.collections[array_index][relative_index] = data
        else:
            self._add_collection()
            # Recurse and try setting again
            self[index] = data

    def __getitem__(self, index):
        """ Gets the data associated with a given index in this array.

        If the index specified is outside of the currently allocated space for
        the array, additional space will be allocated. I'm still not sure if
        this design decision makes sense for __getitem__, but I figured it
        couldn't hurt to stay consistent with __setitem__.

        """
        #TODO For data objects with only one property, allow getting like:
        # a[5] = "Steve"
        # a[5] == "Steve"
        # True
        array_index    = self._get_array_index(index)
        relative_index = self._get_relative_index(index, array_index)
        if array_index < len(self.collections):
            return self.collections[array_index][relative_index]
        else:
            self._add_collection()
            # Recurse and try setting again
            return self[index]

    def close(self):
        """ Closes the associated file object for this array. """
        self.file_object.close()
