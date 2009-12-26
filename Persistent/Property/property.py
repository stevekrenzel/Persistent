from struct import calcsize

class Property:
    """Property class used to define fields of data in Data objects.

    Fields inherit from the Property class to control how data is saved
    and loaded from disk. A property must be represented to the Data object
    using a single 'atomic' struct type. This class allows you determine
    how a single property is read from and written to disk.

    This is useful when you need a property that depends on multiple values,
    such as a string which requires both an int to track its length and
    the actual characters composing the string. See the String implementation
    to learn more about how this works.

    Most properties are fine with the default methods.

    >>> p = Property('f', 0.0)
    >>> p.get_default()
    0.0
    >>> p.unpack(1.0)
    1.0
    >>> p.pack(1.0)
    1.0

    """
    def __init__(self, format, default, key=False, meta=False):
        """ Initializes a new Data property.

        The format follows the struct format described here:
            http://docs.python.org/library/struct.html

        The format must represent exactly one ctype due to the way in which
        the Data class groups all of the properties together. The format can
        however be multiples of that ctype (e.g. 'c' or '10c').

        The default is the default value that this property will be set to.
        When the data is written to disk it will need to be represented in
        some form. The default lets you set what those bits will be.

        The key paramter is used to determine whether or not this field should
        be partof the key in the Data object.

        """

        self.format  = format
        self.key     = key
        self.meta    = meta
        self.default = default
        self.size    = calcsize(self.format)

    def get_default(self, file_object=None):
        """ Returns the default value associated with this property. """

        return self.default

    def unpack(self, value, file_object=None):
        """ Given data passed in, will interpret that data and return
        the interpreted result.

        By default the interpreted result is simply itself.

        """

        return value

    def pack(self, value, file_object=None):
        """ Given a value passed in, will convert the value into data to be
        written to disk. This data will later be consumed by unpack().

        """

        return value
