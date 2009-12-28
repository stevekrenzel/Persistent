from struct import pack, unpack, calcsize
from Persistent.Property import Property, IntegerProperty
from zlib import crc32

class Data:
    """ Add doc strings and kill TODOs """
    _crc_fmt  = "i"
    _crc_size = calcsize(_crc_fmt)
    # TODO add _is_set

    def __init__(self, _parent=None, _bytes=None, _file=None,  **kwargs):
        cls = self.__class__
        if "_props" not in cls.__dict__:
            is_property = lambda x: isinstance(x[1], Property)
            is_key      = lambda x: x[1].is_key
            is_data     = lambda x: x[1].is_data
            get_fmt     = lambda x: "".join(y[1].format for y in x)

            items = filter(is_property, cls.__dict__.items())
            items.sort()

            cls._keys      = filter(is_key, items)
            cls._keys_fmt  = get_fmt(cls._keys)
            cls._keys_size = calcsize(cls._keys_fmt)

            cls._data      = filter(is_data, items)
            cls._data_fmt  = get_fmt(cls._data)
            cls._data_size = calcsize(cls._data_fmt)

            cls._props = cls._keys      + cls._data
            cls._size  = cls._keys_size + cls._data_size + cls._crc_size
        self._file   = _file
        self._parent = _parent
        if _bytes == None:
            for name, property_ in self._props:
                value = kwargs.get(name, property_.get_default(self._file))
                setattr(self, name, value)
        else:
            self.load(_bytes)

    def load(self, bytes):
        a, b, c    = self._keys_size, self._data_size, self._crc_size
        key_bytes  = bytes[0 : a]
        data_bytes = bytes[a : a + b]
        checksum   = bytes[a + b : a + b + c]
        if pack(self._crc_fmt, crc32(bytes[0 : a + b])) != checksum:
            raise Exception("Checksums don't match. Looks like corrupt data")
        keys_vals  = unpack(self._keys_fmt, key_bytes)
        data_vals  = unpack(self._data_fmt, data_bytes)
        values     = keys_vals + data_vals
        for (name, property_), value in zip(self._props, values):
            setattr(self, name, property_.unpack(value, self._file))

    def unload(self):
        keys = [property_.pack(getattr(self, name))
                for name, property_ in self._keys]
        data = [property_.pack(getattr(self, name))
                for name, property_ in self._data]
        keys_bytes = pack(self._keys_fmt, *keys)
        data_bytes = pack(self._data_fmt, *data)
        bytes      = keys_bytes + data_bytes
        checksum   = pack(self._crc_fmt, crc32(bytes))
        return bytes + checksum

    def unload_key(self):
        keys = [property_.pack(getattr(self, name)) \
                for name, property_ in self._keys]
        return pack(self._keys_fmt, *keys)

    def commit(self):
        self._parent.commit(self)

    def __str__(self):
        rep = lambda x: "%s: %s" % (x, getattr(self, x))
        ret = ", ".join(rep(name) for name, property in self._props)
        return "{" + ret + "}"
