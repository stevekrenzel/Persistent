from struct import calcsize
from hashlib import md5
from Persistent.Array.fixed_array import FixedArray

class FixedSet(FixedArray):

    def __init__(self, data, file_name, file_object=None, allocation=1024,
            probe_size=75, address=None):
        FixedArray.__init__(self, data, file_name, file_object, allocation,
            address)
        allocation      = self.size/self.data.size_
        self.probe_size = min(allocation, probe_size)
        self.empty_cell = chr(255) * self.data.size_
        self.range      = allocation - self.probe_size + 1
        self.long_sz    = calcsize("q")
        # TODO Write all construction information to disk

    def set(self, data):
        bytes        = data.unload_key() if data._keys else data.unload()
        address, raw = self._find_bytes(bytes)
        index        = self._find_by_bytes(bytes, raw)
        if index != None:
            # We only write data if this has keys because otherwise
            # we've already confirmed that these bits exist on disk
            if data._keys:
                self._commit(data, address=address + index)
            return True
        index = self._find_by_bytes(self.empty_cell, raw)
        if index != None:
            self._commit(data, address=address + index)
            return True
        return False

    def get(self, data):
        bytes = data.unload_key() if data._keys else data.unload()
        address, raw = self._find_bytes(bytes)
        index = self._find_by_bytes(bytes, raw)
        if index != None:
            return self.data(self, raw[index : index + self.data.size_])
        return None

    def _commit(self, data, bytes=None, address=None):
        if address == None:
            return self.set(data)
        if bytes == None:
            bytes = data.unload()
        self.file_object.seek(address)
        self.file_object.write(bytes)

    def _find_bytes(self, bytes):
        address = self._get_address(bytes)
        self.file_object.seek(address)
        return (address,
            self.file_object.read(self.data.size_ * self.probe_size))

    def _find_by_bytes(self, data_bytes, lookup_bytes):
        if data_bytes not in lookup_bytes:
            return None
        index = lookup_bytes.find(data_bytes)
        while index != -1:
            if index % self.data.size_ == 0:
                return index
            index = lookup_bytes.find(data_bytes, index + 1)
        return None

    def _get_address(self, bytes):
        slot    = int(md5(bytes).hexdigest(), 16) % self.range
        offset  = slot * self.data.size_
        return self.address + self.long_sz + offset

    def __contains__(self, data):
        return self.get(data) != None
