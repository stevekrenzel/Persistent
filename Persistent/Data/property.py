from struct import calcsize

class Property:
    def __init__(self, format, default, key=False):
        self.format  = format
        self.key     = key
        self.default = default
        self.size    = calcsize(self.format)

    def get_default(self, file=None):
        return self.default

    def unpack(self, value, file=None):
        return value

    def pack(self, value, file=None):
        return value

class IntegerProperty(Property):
    def __init__(self, default=0, key=False):
        Property.__init__(self, "I", default, key) 
