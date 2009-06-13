###############################################################################
# The author or authors of this code dedicate any and all copyright interest in
# this code to the public domain. We make this dedication for the benefit of
# the public at large and to the detriment of our heirs and successors. We
# intend this dedication to be an overt act of relinquishment in perpetuity of
# all present and future rights to this code under copyright law.
###############################################################################

from struct     import pack, unpack, calcsize
from Persistent import KeyValueList

class PersistentMap:
    """ The PersistentMap is a hashmap with a predefined number of buckets,
    and each bucket holds the address of a KeyValueList. This list is where
    the keys and values are actually stored.
    TODO: Create set that uses lists instead of key/value lists.

    The bucket for the map is never resized and is initiated on map creation.

    """
    def __init__(self, file_object, key_format, value_format, number_of_keys, address=None):
        """This initiates the map instance. It accepts a key and value format
        following the standard struct format. The number_of_keys is the bucket
        size.

        """
        self.file_object     = file_object
        self.key_format      = key_format
        self.value_format    = value_format
        self.num_of_keys     = number_of_keys
        self.address_format  = "I"
        self.address_size    = calcsize(self.address_format)
        self.address         = address

        # We need a way to specify that a particular bucket has no list
        # associated with it, so we use the largest integer as an invalid
        # address.
        self.invalid_address = 2 ** (8*self.address_size) -1

        # If no address is specified we allocate the buckets at the end of
        # the file.
        if address == None:
            self.file_object.seek(0, 2)
            self.address  = self.file_object.tell()
            map_size      = number_of_keys * self.address_size

            # We write the buckets half a megabyte at a time, this keeps
            # the ram usage pretty small while writing large numbers of
            # buckets fairly quickly.
            block_size    = 512 * 1024
            keys_in_block = block_size / self.address_size

            # We create a block of data filled with invalid addresses
            zeroed_block  = pack(self.address_format * keys_in_block, *([self.invalid_address] * keys_in_block))

            # Write the blocks to disk
            for i in xrange(map_size / block_size):
                self.file_object.write(zeroed_block)

            # The last block won't likely be a full block, so we create a
            # special block for the last one.
            last_block_size    = map_size % block_size
            keys_in_last_block = last_block_size / self.address_size
            zeroed_last_block  = pack(self.address_format * keys_in_last_block, *([self.invalid_address] * keys_in_last_block))
            self.file_object.write(zeroed_last_block)

    def set(self, key, value):
        """ Takes a key and value and stores it in the map. If the key
        already exists, it will be replaced.

        """
        # Grab the list that should contain the key
        key_vals = self.__get_key_value_list__(key)

        # If there is no list for the bucket, we create one
        if key_vals is None:
            key_vals = self.__make_list__(self.file_object, self.key_format, self.value_format)

            # We have to put something in the list so that we have the address
            # of the head to insert in the bucket.
            key_vals.set(key, value)

            # Add the list to the bucket
            self.__set_key_value_list__(key, key_vals)
        else:
            key_vals.set(key, value)

    def get(self, key):
        """Given a key, this will return the associated value for that key.
        
        """
        key_vals = self.__get_key_value_list__(key)
        if key_vals is not None:
            return key_vals.get(key)

    def __get_key_value_list__(self, key):
        position = self.__get_hash__(key) 
        self.file_object.seek(position)
        address = unpack(self.address_format, self.file_object.read(self.address_size))[0]
        if address != self.invalid_address:
            return self.__make_list__(self.file_object, self.key_format, self.value_format, address)

    def __set_key_value_list__(self, key, key_value_list):
        position = self.__get_hash__(key) 
        self.file_object.seek(position)
        self.file_object.write(pack(self.address_format, key_value_list.head.address))

    def __get_hash__(self, key):
        return self.address + ((hash(key) % self.num_of_keys) * self.address_size)

    def __make_list__(self, file_object, key_format, value_format, address=None):
        return KeyValueList(file_object, key_format, value_format, address)

