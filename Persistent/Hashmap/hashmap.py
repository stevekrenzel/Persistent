###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from Persistent.Data.test import Data
from Persistent import Hashset

class Hashmap(Hashset):
    """We just give it a different name for cleaner code right now."""

    def set(self, data):
        self.add(data)

    def __setitem__(self, key, value):
        if len(self.data._keys) != 1 or len(self.data._names) != 2:
            raise Exception()
        key_name = self.data._names[0]
        val_name = self.data._names[1]
        kwargs = {key_name : key, val_name : value}
        self.set(self.data(**kwargs))

    def __getitem__(self, key):
        if len(self.data._keys) != 1:
            raise Exception()
        key_name = self.data._names[0]
        kwargs = {key_name : key}
        return self.get(self.data(**kwargs))
