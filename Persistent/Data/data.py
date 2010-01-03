from struct import pack, unpack, calcsize
from Persistent.Property import Property, IntegerProperty
from zlib import crc32

class Data:
    """ Data class is responsible for managing a series of related properties.
    Effectively it is an object that can be written to and read from disk.

    Objects inherit from Data to define the fields that they would like stored
    in various containers (i.e. Hashmap, Array, etc...). Think of this as the
    schema of your data model.

    For instance, you could define a User object that has a username and
    password like:

    class User(Data):
        username = StringProperty(length=25)
        password = StringProperty(length=25)

    Some containers, such as a hashmap, require a key to be present (because
    a hashmap maps keys to values). You can specifiy which property(ies) are
    keys by passing "key=True" in the init args. Here is an example User object
    where the username is the key.

    class User(Data):
        username = StringProperty(length=25, key=True)
        password = StringProperty(length=25)

    Now the hashmap can look up the User object given only the username.

    >>> from Persistent import StringProperty
    >>> class User(Data):
    ...   username = StringProperty(length=25)
    ...   password = StringProperty(length=25)
    ...
    >>> user = User()
    >>> user.load(user.unload())
    >>> user.username == None
    True
    >>> user.password == None
    True
    >>> user.username = "Steve"
    >>> new_user = User(_bytes=user.unload())
    >>> new_user.username
    'Steve'
    >>> new_user.password == None
    True

    >>> class User(Data):
    ...   username = StringProperty(length=5, key=True)
    ...   password = StringProperty(length=25)
    ...
    >>> user = User()
    >>> user.username = "Steve"
    >>> user.password = "password"
    >>> user.unload_key()
    '\\x01\\x05\\x00\\x00\\x00Steve'
    >>> print user
    {username: Steve, password: password}

    """

    # The checksum is simply an int, this describes the format and size
    _crc_fmt  = "i"
    _crc_size = calcsize(_crc_fmt)

    def __init__(self, _container=None, _bytes=None, _file=None,  **kwargs):
        """ Initializes a new Data object

        _container is the container that is storing these Data objects.
        This can be an array, set, or any other container available.

        _bytes are the bytes for the properties of this Data object. When
        you read bytes from disk and want to instantiate a Data object, you
        set them here. When _bytes is None, each property is simply set
        to None.

        _file is the open file handle that the bytes for this data object
        are being written to.

        """
        # We use cls just so we don't have to keep writing self.__class__
        cls = self.__class__

        # If the class properties haven't been initialized yet, initialize
        # them.
        if "_props" not in cls.__dict__:
            is_property = lambda x: isinstance(x[1], Property)
            is_key      = lambda x: x[1].is_key
            is_data     = lambda x: x[1].is_data

            # Get all of the class fields that are properties and sort them
            # by name. It is important to sort them by name so that they
            # are always in the same order. By default dict.items() might
            # be in a different order in different versions of python. The
            # order determines the order of the bytes on disk as well.
            cls._props = filter(is_property, cls.__dict__.items())
            cls._props.sort()

            # We then get a list of all of the keys for this Data object
            cls._keys = filter(is_key, cls._props)
            # And we get a list of all non-keys for this Data object.
            cls._data = filter(is_data, cls._props)

            # We put the keys before the data so that the bytes on disk always
            # start with the key bytes, if there are any. This is useful for
            # some containers when doing lookups.
            cls._props = cls._keys + cls._data
            cls._size  = sum(prop.size for name, prop in cls._props) + \
                         cls._crc_size
        self._file   = _file
        self._container = _container

        # If no bytes have been specified, then we aren't loading an object
        # off of disk, but rather intializing a new empty object. We set
        # the values for all of the properties to None by default, unless
        # a value was specified in the kwargs for the property.
        # For instance, when dealing with:
        #
        # class User(Data):
        #   username = StringProperty(length=25)
        #   password = StringProperty(length=25)
        #
        # We can initialize a new object by speifiying the bytes that were
        # written to disk (that is the 'else' in this if-else statement),
        # but if we instead are initializing a new object, we can do so like:
        #
        # u = User()
        #
        # In this instance, u.username is None and u.password is None. If we
        # instead initialize it like:
        #
        # u = User(username="Steve")
        #
        # Then u.username is "Steve" and u.password is "None"
        if _bytes == None:
            for name, property_ in self._props:
                value = kwargs.get(name, None)
                setattr(self, name, value)
        else:
            # If bytes are specified, we initialize the object using those
            # bytes
            self.load(_bytes)

    def load(self, bytes):
        """ Sets the values for the attributes of the object based on the
        bytes passed in. In other words, deserializes the object.

        """

        # We iterate through each property and tell that property to
        # unpack its respective bytes.
        start = 0
        for name, property_ in self._props:
            # We set data to the appropaite range of bytes for that
            # given property
            data = bytes[start : start + property_.size]

            # Then we unpack the value from the bytes and set the object's
            # respective attribute to this value
            setattr(self, name, property_.unpack(data, self._file))

            # When we're done with this property, we update the new start
            # position for the bytes for the next property
            start += property_.size
        # The last few bytes are the bytes for the checksum. We just make
        # sure that the checksum is what it is supposed to be. If it's not
        # then we throw an exception.
        checksum = bytes[start : start + self._crc_size]
        if pack(self._crc_fmt, crc32(bytes[0 : -self._crc_size])) != checksum:
            raise Exception("Checksums don't match. Looks like corrupt data")

    def unload(self):
        """ Takes the values for the attributes of the object and converts
        these values to a series a bytes that can be written to disk. In
        other words, it serializes the object.

        """
        # Iterate through each property and join the packed bytes
        bytes = "".join(property_.pack(getattr(self, name))
                        for name, property_ in self._props)
        # Append the checksum to the end of the bytes
        checksum = pack(self._crc_fmt, crc32(bytes))
        return bytes + checksum

    def unload_key(self):
        """ Takes the values for the attributes of the object that
        are keys and converts them to bytes. This is useful when
        you've got a long series of bytes and want to see if the key
        is present somewhere in them.

        """
        return "".join(property_.pack(getattr(self, name))
                       for name, property_ in self._keys)

    def commit(self):
        """ This saves the data object in whatever its container is. This
        way, once you get a Data object from a container, you can pass it
        around and when you're done modifying it, just call it's commit()
        method instead of needing to know what container it came from
        and using the container's methods to explicitly update it.

        """
        # TODO the old object will still be present in the container,
        # This is only a problem for containers that use key->vals and
        # the key has been modified.
        # This is a known bug. To fix this, delete the old object first.
        # Delete support isn't implemented yet.
        self._container.commit(self)

    def __str__(self):
        """ Just outputs the Data object in a human readable format. """
        rep = lambda x: "%s: %s" % (x, getattr(self, x))
        ret = ", ".join(rep(name) for name, property in self._props)
        return "{" + ret + "}"
