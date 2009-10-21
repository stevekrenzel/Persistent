###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize

class Data:

    def __init__(self, format, file_object=None, address=None, bytes=None):
        self.file_object        = file_object
        format                  = format.split(",")
        self.format, self.names = zip(*[i.split(":") for i in format])
        self.format             = "".join(self.format)
        self.size               = calcsize(self.format)
        self.address            = address
        self.empty_cell         = chr(255) * self.size
        self.bytes              = bytes or self.empty_cell
        self.values             = {}

        if self.file_object != None:
            # We allocate space at the end of the file if there is no address
            # If you provide a file object, you've got to provide an address
            # or we make space for you.
            if self.address == None:
                # Seek to the end of the file and write the data
                self.file_object.seek(0, 2)
                self.address = self.file_object.tell()
                self.file_object.write(self.bytes)
            elif self.bytes == self.empty_cell:
                # If we haven't been given the bytes for this data,
                # read it in
                self.file_object.seek(self.address)
                self.bytes = self.file_object.read(self.size)

        values = unpack(self.format, self.bytes)
        for name, value in zip(self.names, values):
            self.values[name] = value

    def __getitem__(self, name):
        return self.values[name]

    def __setitem__(self, name, value):
        self.values[name] = value
        self.set(self.values)

    def set(self, values):
        # Store the value in memory for quick access later
        self.values = values
        self.bytes  = pack(self.format, *[values[name] for name in self.names])

        if self.file_object != None:
            # Seek to our spot on disk and write the new value
            self.file_object.seek(self.address)
            self.file_object.write(self.bytes)

    def __eq__(self, other):
        return self.values == other.values if other != None else None

    def __str__(self):
        return str(self.values)

    def __cmp__(self, other):
        return cmp(self.values, other.values if other != None else None)

    def get(self):
        return self.values

if __name__ == "__main__":
    import os

    filename = "data_test.db"
    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()

    #db     = open(filename, "r+b")
    format = "I:age, 20s:name"
    age    = 10
    name   = "Steve"
    data   = Data(format)
    print data
    data["age"]  = age
    data["name"] = name
    print data
