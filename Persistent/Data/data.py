from struct import pack, unpack, calcsize
from Persistent.Property import Property, IntegerProperty
from zlib import crc32

class Data:
    """ Add doc strings and kill TODOs """
    #TODO add byte to determine what vals are set and which aren't
    #TODO add crc32
    def __init__(self, _parent=None, _bytes=None, _file=None,  **kwargs):
        if "_names" not in self.__class__.__dict__:
            # TODO change _set IntegerProperty  to BoolProperty
            meta_names = ["_crc32", "_is_set"]
            meta_props = [IntegerProperty(), IntegerProperty()]

            # TODO we have to treat keys, props, and meta as 3 different groups
            # the bytes must be appended after packing due to byte alignment
            # This can also be achieved by storing the 3 formats, packing the properties
            # and appending the bytes together
            is_property = lambda x: isinstance(x[1], Property)
            key_tup     = lambda x: (not x[1].key, x[0])
            key_cmp     = lambda x, y: cmp(key_tup(x), key_tup(y))
            items       = filter(is_property, self.__class__.__dict__.items())
            names       = sorted(items, key_cmp)

            self.__class__._names    = names
            self.__class__._key_fmt  = "".join(x[1].format for x in names if x[1].key == True)
            self.__class__._format   = "".join(x[1].format for x in names)
            self.__class__.size_     = calcsize(self._format)
            self.__class__._keys     = self.__class__._key_fmt != ""
        self._file   = _file
        self._parent = _parent
        if _bytes == None:
            for name, property_ in self._names:
                value = kwargs.get(name, property_.get_default(self._file))
                setattr(self, name, value)
        else:
            self.load(_bytes)

    def load(self, bytes):
        values = unpack(self._format, bytes)
        for (name, property_), value in zip(self._names, values):
            setattr(self, name, property_.unpack(value, self._file))

    def unload(self):
        properties = [property_.pack(getattr(self, name))
                      for name, property_ in self._names]
        bytes = pack(self._format, *properties)
        return bytes

    def unload_key(self):
        # TODO Can we safely unload key due to pack padding?
        properties = [property_.pack(getattr(self, name)) \
                      for name, property_ in self._names
                      if property_.key == True]
        return pack(self._key_fmt, *properties)

    def commit(self):
        self._parent.commit(self)

    def __str__(self):
        rep = lambda x: "%s: %s" % (x, getattr(self, x))
        ret = ", ".join(rep(name) for name, property in self._names)
        return "{" + ret + "}"
