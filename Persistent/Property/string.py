###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize
from Persistent.Property import Property

class StringProperty(Property):
    def __init__(self, length, default="", key=False):
        self.length = length
        # We add 4 to the length, which uses 4 bytes to represent
        # an int which tracks the length of the string. Pascal strings
        # were simply too short, with a max length of 255 chars.
        Property.__init__(self, "%ds" % (length + 4), default, key)

    def unpack(self, value, file=None):
        fmt = "I%ds" % (self.length)
        length, string = unpack(fmt, value)

    def pack(Self, value, file=None):
        if len(value) > self.length:
            value = value[:self.length]
        fmt = "I%ds" % (self.length)
        length, string = unpack(fmt, len(value), value)
