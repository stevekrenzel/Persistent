###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct import pack, unpack, calcsize

class Data:

    def __init__(self, file_object, format, address=None):
        self.file_object = file_object
        self.format      = "".join(i.split(":")[0].strip() for i in format.split(","))
        self.names       = [i.split(":")[1].strip() for i in format.split(",")]
        self.size        = calcsize(self.format)
        self.address     = address
        self.value       = None

        # We allocate space at the end of the file if there is no address
        if self.address == None:
            # Zero out the values
            self.value = list(unpack(self.format, chr(0)*self.size))

            # Seek to the end of the file and write the data
            self.file_object.seek(0, 2)
            self.file_object.write(pack(self.format, *self.value))
            self.address = self.file_object.tell() - self.size
        else:
            # Seek to the start of the node.
            self.file_object.seek(self.address)

            # Read in the data and store it
            self.value = list(unpack(self.format, self.file_object.read(self.size)))

    def __getitem__(self, name):
        return self.value[self.names.index(name)]

    def __setitem__(self, name, value):
        self.value[self.names.index(name)] = value
        self.set(*self.value)

    def set(self, *value):
        # Store the value in memory for quick access later
        self.value = list(value)

        # Seek to our spot on disk and write the new value
        self.file_object.seek(self.address)
        self.file_object.write(pack(self.format, *self.value))

    def get(self):
        return self.value

if __name__ == "__main__":
    import os

    filename = "fixed_width_test.db"
    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()

    db     = open(filename, "r+b")
    format = "I:age, 20s:name"
    age    = 10
    name   = "Steve"
    data   = Data(db, format)
    print data["age"]
    print data["name"]
    data["age"]  = age
    data["name"] = name
    print data["age"]
    print data["name"]
    db.close()
    db = open(filename, "r+b")
    data = FixedWidthData(db, format, data.address)
    print data["age"]
    print data["name"]
    os.remove(filename)
