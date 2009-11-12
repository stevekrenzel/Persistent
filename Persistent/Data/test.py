from struct import pack, unpack, calcsize
import pdb
from Persistent.Data.property import Property
from itertools import izip

class Data:
    #TODO add byte to determine what vals are set and which aren't
    #TODO add crc32 
    def __init__(self, _parent=None, _bytes=None, _file=None,  **kwargs):
        if "_names" not in self.__class__.__dict__:
            names      = []
            properties = []
            key        = None
            size       = 0
            format     = "" 
            for name, property in sorted(self.__class__.__dict__.items()):
                if isinstance(property, Property): 
                    if property.key == True:
                        key = (name, property)
                    else:
                        names.append(name)
                        properties.append(property)
            if key != None:
                names      = [key[0]] + names
                properties = [key[1]] + properties
            self.__class__._names      = names
            self.__class__._properties = properties
            self.__class__._key        = key
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
        properties = list(property.pack(getattr(self, name)) \
                      for name, property in izip(self._names, self._properties))
        return pack(self._format, *properties)

    def commit(self):
        self._parent.__commit__(self)

    def __str__(self):
        ret = ", ".join("%s: %s"%(name, getattr(self, name)) for name in self._names)
        return "{" + ret + "}" 

