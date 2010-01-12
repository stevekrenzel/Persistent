from Persistent import Hashset

class Hashmap(Hashset):
    """ Hashmap is really a hashset, we just give it a different.

    >>> from Persistent import Data, StringProperty
    >>> class User(Data):
    ...   username = StringProperty(length=25, key=True)
    ...   password = StringProperty(length=25)
    ...
    >>> m = Hashmap(User, "hashmap_doctest.db")
    >>> for i in xrange(100):
    ...   m[str(i)] = str(i) + "!"
    >>> for i in xrange(100):
    ...   if m[str(i)] != str(i) + "!":
    ...     print 'Failed to match %s.' % (i)
    >>> for i in xrange(100):
    ...   m.set(User(username=str(i), password=str(i) + "!"))
    >>> for i in xrange(100):
    ...   u = m.get(User(username=str(i)))
    ...   if u.password != str(i) + "!":
    ...     print 'Failed to match %s.' % (i)
    >>> import os
    >>> os.remove("hashmap_doctest.db")

    """

    def set(self, data):
        """ Adds a data object to the hashmap. """
        # This attribute is so that the hashset knows what bytes from the
        # data are important
        data._is_map = True
        self.add(data)

    def get(self, data, default=None):
        """ Retrieve a data object from the hashmap.
        If the data isn't found, default is returned.

        """
        # This attribute is so that the hashset knows what bytes from the
        # data are important
        data._is_map = True
        return Hashset.get(self, data, default)

    def __setitem__(self, key, value):
        """ Adds a key value mapping to the hashmap.

        This only works if the data object that the hashmap was
        initialized with has exactly one key and one property.

        i.e. You can do:
                users["Steve"] = "password"
             instead of:
                users.set(User(username="Steve", password="password")))

        """
        if len(self.data._keys) != 1 or len(self.data._props) != 2:
            raise Exception()
        key_name = self.data._props[0][0]
        val_name = self.data._props[1][0]
        kwargs = {key_name : key, val_name : value}
        self.set(self.data(**kwargs))

    def __getitem__(self, key):
        """ Retrieves a key value mapping from the hashmap.
        If the key doesn't exists, None is returned.

        This only works if the data object that the hashmap was
        initialized with has exactly one key and one property.

        i.e. You can do:
                users["Steve"] == "password"
             instead of:
                users.get(User(username="Steve")).password == "password"

        """
        if len(self.data._keys) != 1 or len(self.data._props) != 2:
            raise Exception()
        key_name = self.data._props[0][0]
        val_name = self.data._props[1][0]
        kwargs   = {key_name : key}
        data     = self.get(self.data(**kwargs))
        if data != None:
            return getattr(data, val_name)
        return None
