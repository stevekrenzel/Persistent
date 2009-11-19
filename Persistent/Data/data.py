###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize
from Persistent.Data.property import Property
from itertools import izip

class Data:
    #TODO add byte to determine what vals are set and which aren't
    #TODO add crc32
    def __init__(self, _parent=None, _bytes=None, _file=None,  **kwargs):
        if "_names" not in self.__class__.__dict__:
            names      = []
            properties = []
            keys       = []
            key_names  = []
            key_fmt    = ""
            size       = 0
            format     = ""
            for name, property in sorted(self.__class__.__dict__.items()):
                if isinstance(property, Property):
                    if property.key == True:
                        keys.append((name, property))
                        key_fmt += property.format
                    else:
                        names.append(name)
                        properties.append(property)
            if len(keys) != 0:
                # We require the key bits to be at the start of the data
                key_names  = [k[0] for k in keys]
                key_props  = [k[1] for k in keys]
                names      = key_names + names
                properties = key_props + properties
            self.__class__._names      = names
            self.__class__._properties = properties
            self.__class__._keys       = set(key_names) if len(keys) != 0 else None
            self.__class__._key_fmt    = key_fmt
            self.__class__._size       = sum(p.size for p in properties)
            self.__class__._format     = "".join(p.format for p in properties)
        self._file = _file
        self._parent = _parent
        if _bytes == None:
            for name, property in izip(self._names, self.__class__._properties):
                setattr(self, name, kwargs.get(name, property.get_default(self._file)))
        else:
            self.load(_bytes)

    def load(self, bytes):
        values = unpack(self._format, bytes)
        for name, value, property in izip(self._names, values, self._properties):
            setattr(self, name, property.unpack(value, self._file))

    def unload(self):
        properties = [property.pack(getattr(self, name)) \
                      for name, property in izip(self._names, self._properties)]
        return pack(self._format, *properties)

    def unload_key(self):
        properties = [property.pack(getattr(self, name)) \
                      for name, property in izip(self._names, self._properties)
                      if name in self._keys]
        return pack(self._key_fmt, *properties)

    def commit(self):
        self._parent.commit(self)

    def __str__(self):
        ret = ", ".join("%s: %s"%(name, getattr(self, name)) for name in self._names)
        return "{" + ret + "}"
