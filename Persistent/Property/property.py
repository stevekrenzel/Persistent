from struct import calcsize, unpack, pack

class Property:
    """ Property class is used to define fields of data in Data objects.

    Fields inherit from the Property class to control how data is saved
    and loaded from disk via the pack and unpack methods.

    Most simple properties are fine with the default methods, but more
    complex types, such as strings (which require an int and chars),
    will need custom pack and unpack methods.

    Also note that the value None is supported. Each property has an extra
    byte that tracks whether or not the value is actually set.

    """
    def __init__(self, format, key=False):
        """ Initializes a new Data property.

        The format follows the struct format described here:
            http://docs.python.org/library/struct.html

        The key paramter is used to determine whether or not this field should
        be part of the key in the Data object.

        The default value to be written to disk is simply a series of
        nulled bytes.

        The first byte of the data is 0 if the value has not been set
        (i.e. is None), or 1 otherwise. This lets us do things like write 0
        to disk for an int, and read it back knowing that it is really a 0
        and not None.
        """

        # We add 1 to the size for the is_set byte
        self.format  = format
        self.size    = 1 + calcsize(self.format)
        self.default = chr(0) * self.size
        self.is_key  = key
        self.is_data = not self.is_key

    def unpack(self, bytes, file_object=None):
        """ Given bytes passed in, the first byte is read to determine if the
        associated value is None or has been set. If it has been set, we
        unpack the bytes according to the specified format.

        >>> p = Property('i', 0)
        >>> p.unpack('\\x00\\x00\\x00\\x00\\x00')
        >>> p.unpack('\\x01\\x00\\x00\\x00\\x00')
        0

        """

        is_set = ord(bytes[0]) != 0
        if is_set:
            return unpack(self.format, bytes[1:])[0]
        return None

    def pack(self, value, file_object=None):
        """ Given a value passed in, will convert the value into bytes to be
        written to disk. This data will later be consumed by unpack().

        If the value is None, then the default bytes are returned. The default
        bytes have a 0 byte as their first byte. This will be interpreted by
        unpack() as being a None value.

        If the value is not None, the first byte is set to 1 and the value is
        formatted to bytes. Since the first byte is 1, unpack() will interpret
        the remaining bytes as valid data.

        >>> p = Property('i', 0)
        >>> p.pack(None)
        '\\x00\\x00\\x00\\x00\\x00'
        >>> p.pack(0)
        '\\x01\\x00\\x00\\x00\\x00'

        """
        if value == None:
            return self.default
        return chr(1) + pack(self.format, value)
