from Persistent.Property import Property

class IntegerProperty(Property):
    """ The IntegerProperty class is used to represent integer fields
    in Data objects.

    >>> i = IntegerProperty(4294967295)
    >>> i.get_default()
    4294967295

    """

    def __init__(self, default=0, key=False):
        """ Initializes the IntegerProperty. """

        Property.__init__(self, "i", default, key)

