###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize

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
