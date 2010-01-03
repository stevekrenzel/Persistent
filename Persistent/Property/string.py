from struct import pack, unpack, calcsize
from Persistent.Property import Property

class StringProperty(Property):
    """ The StringProperty class is used to represent fixed length strings in
    Data objects.

    """

    def __init__(self, length, **kwargs):
        """ Initializes the String Property.

        The length parameter determines the maximum length of the
        string. The string itself may be smaller than this and any bytes
        left over will be null'd.

        For example, creating a StringProperty with length 10, but packing
        a value of length 3 will result in the 3 characters being written
        followed by 7 null bytes.

        """

        self.length = length
        # An int tracks the length of the string. Pascal strings
        # were simply too short, with a max length of 255 chars.
        Property.__init__(self, "I%ds" % (length), **kwargs)

    def unpack(self, bytes, file_object=None):
        """ Given a series of bytes, unpack will interpret the first byte as a
        boolean to see if the string is None or an actual value. The
        remaining bytes are interpreted as an int representing the length of
        the string, followed by the bytes representing the string.


        >>> s = StringProperty(15)
        >>> s.unpack(s.pack(None))

        >>> s = StringProperty(10)
        >>> s.unpack(s.pack('Persistent'))
        'Persistent'

        >>> s = StringProperty(5)
        >>> s.unpack(s.pack('Persistent'))
        'Persi'

        """

        is_set = ord(bytes[0]) != 0
        if is_set:
            length, string = unpack(self.format, bytes[1:])
            return string[:length]
        return None

    def pack(self, value, file_object=None):
        """ Given a string, pack() will convert the string into bytes
        representing three things. 1) The first byte is zero if the value
        is None, otherwise it is one 2) The length of the string 3) The bytes
        representing the characters of the string.

        Note that if the value is greater than the maximum length specified
        when the StringProperty was created, any overflow will be ignored.

        >>> s = StringProperty(5)
        >>> s.pack(None)
        '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'

        >>> s = StringProperty(15)
        >>> s.pack('Persistent')
        '\\x01\\n\\x00\\x00\\x00Persistent\\x00\\x00\\x00\\x00\\x00'

        >>> s = StringProperty(10)
        >>> s.pack('Persistent')
        '\\x01\\n\\x00\\x00\\x00Persistent'

        >>> s = StringProperty(5)
        >>> s.pack('Persistent')
        '\\x01\\x05\\x00\\x00\\x00Persi'

        """

        if value == None:
            return self.default
        value = value[:self.length]
        return chr(1) + pack(self.format, len(value), value)
