from struct import pack, unpack, calcsize
from Persistent.Property import Property

class StringProperty(Property):
    """ The StringProperty class is used to represent fixed length strings in
    Data objects.

    >>> s = StringProperty(10, 'default')
    >>> s.get_default()
    'default'

    """

    def __init__(self, length, default="", key=False):
        """ Initializes the String Property.

        The length parameter determines the maximum length of the
        string. The string itself may be smaller than this and any bytes
        left over will be null'd.

        For example, creating a StringProperty with length 10, but packing
        a value of length 3 will result in the 3 characters being written
        followed by 7 null bytes.

        """

        self.length = length
        # We add 4 to the length, which uses 4 bytes to represent
        # an int which tracks the length of the string. Pascal strings
        # were simply too short, with a max length of 255 chars.
        # We can't do something like "I10s" because Data expects the
        # properties to be represented by exactly one ctype, and "I10s" uses
        # two ("I" and "s").
        int_len = calcsize("I")
        Property.__init__(self, "%ds" % (length + int_len), default, key)

    def unpack(self, value, file_object=None):
        """ Given a series of bytes, will interpret those bytes as an int
        representing the length of a string, followed by the bytes for the
        string. It will then return the determined string.

        >>> s = StringProperty(15)
        >>> s.unpack(s.pack('Persitent'))
        'Persistent'

        >>> s = StringProperty(10)
        >>> s.unpack(s.pack('Persistent'))
        'Persistent'

        >>> s = StringProperty(5)
        >>> s.unpack(s.pack('Persistent'))
        'Persi'

        """

        fmt = "I%ds" % (self.length)
        length, string = unpack(fmt, value)
        return string[:length]

    def pack(self, value, file_object=None):
        """ Given a string, pack() will convert the string into bytes
        representing the length of the string followed by the bytes
        representing the characters of the string. These bytes will then be
        returned to be written to disk. These bytes will later be consumed by
        unpack().

        Note that if the value is greater than the maximum length specified
        when the StringProperty was created, any overflow will be ignored.

        >>> s = StringProperty(15)
        >>> s.pack('Persistent')
        '\n\x00\x00\x00Persistent\x00\x00\x00\x00\x00'

        >>> s = StringProperty(10)
        >>> s.pack('Persistent')
        '\n\x00\x00\x00Persistent'

        >>> s = StringProperty(5)
        >>> s.pack('Persistent')
        ''\x05\x00\x00\x00Persi'

        """

        if len(value) > self.length:
            value = value[:self.length]
        fmt = "I%ds" % (self.length)
        return pack(fmt, len(value), value)
