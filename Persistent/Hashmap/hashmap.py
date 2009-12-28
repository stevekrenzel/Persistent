from Persistent import Hashset

class Hashmap(Hashset):
    """We just give it a different name for cleaner code right now."""

    def set(self, data):
        self.add(data)

    def __setitem__(self, key, value):
        if len(self.data._keys) != 1 or len(self.data._props) != 2:
            raise Exception()
        key_name = self.data._props[0][0]
        val_name = self.data._props[1][0]
        kwargs = {key_name : key, val_name : value}
        self.set(self.data(**kwargs))

    def __getitem__(self, key):
        if len(self.data._keys) != 1:
            raise Exception()
        key_name = self.data._props[0][0]
        kwargs = {key_name : key}
        return self.get(self.data(**kwargs))
