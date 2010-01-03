from Persistent.Property import Property

class IntegerProperty(Property):
    """ The IntegerProperty class is used to represent integer fields
    in Data objects.

    """

    def __init__(self, **kwargs):
        """ Initializes the IntegerProperty. """

        Property.__init__(self, "i", **kwargs)
