from Persistent                   import DynamicCollection
from Persistent.Hashset.fixed_set import FixedSet

class Hashset(DynamicCollection):
    """ Hashset is a dynamically growing set implementation. The set elements
    are data objects.

    The behaviour of this set is similar to most standard sets. You add
    elements to the set, and get them, in constant time. As more space is
    needed, it will automatically be allocated.

    Adding an element should only fail if you run out of disk space.

    The implementation details of this set are different than most sets. In
    fact, to my knowledge, it is an entirely new way to implement sets.

    In a typical set, when we run out of space, we allocate twice as much
    space, re-hash all of the elements of the old set into the new set, then
    delete the old space.

    For example, we might start off allocating enough space for 5 values:

    _ _ _ _ _

    And add three values:

    _ 52 13 _ 95

    Now we try to add a 4th value and get a collision, so we must resize.

    First we allocate twice as much space

    _ _ _ _ _ _ _ _ _ _

    Then we iterate through every value in our old set and insert it into our
    new set:

    95 _ _ _ 13 _ _ 52 _ _

    Then we add our 4th value:

    95 _ _ 37 13 _ _ 52 _ _

    Finally, we delete the old data.

    This has some nice characteristics such as constant time access, but
    reading in all of our data and reinserting it into a new set just takes
    too long when you're dealing with harddrives. If you've got a 2 terabyte
    set, do you really want to rehash 2TB worth of data just so you can
    continue adding values? It would take forever.

    Instead, this hashset implementation performs constant time resizes, very
    similarly to the Peristent Array implementation.

    The way our algorithm works is as follows:

    Initially allocate enough space for 5 values:

    _ _ _ _ _

    And add three values:

    _ 52 13 _ 95

    Now we try to add a 4th value and get a collosion, so we must resize.

    We don't touch the old set, but allocate space for a new set:

    set 1: _  52 _  13 _  95
    set 2: _  _  _  _  _  _  _  _  _  _

    Then we add our 4th value to the new set:

    set 1: _  52 _  13 _  95
    set 2: _  _  _  37 _  _  _  _  _  _

    We continue adding values:

    set 1: _  52 _  13 _  95
    set 2: 40 _  21 37 13 _  89 _  47 29

    Once set 2 is full, we allocate space for a third set and keep adding values:

    set 1: _  52 _  13 _  95
    set 2: 40 _  21 37 13 _  89 _  47 29
    set 3: _  17 _  _  37 66 _  34 59 76 _  92 _  07 30 68 99 _ 89 _

    This has some nice charactersics. Not only are inserts constant time, but
    resizing is also constant time.

    When we want to check if something is in this hashset, we first check set3,
    then set2, then set 1. Now you're thinking that because the number of sets
    we have to check grows with the number of values we have in the set, that
    getting a value is no longer constant time. This however is false, and
    getting items is still constant time.

    It is constant time because set 3 has a 57% chance of containing the
    value, set 2 has a 28%, and set 1 has a 14% chance of containing the value.

    As we add more and more sets, it turns out that the expected number of
    lookups is only two, which is a constant.

    Note that this only holds true if the majority of your lookups are actually
    present in the set. If you frequently look for things that aren't in the
    set, then the average lookup time will be closer to lg(N).

    I'm willing to make this tradeoff. There are many use cases where the
    majority of lookups are in fact in the set (or map, which uses this set
    implementation), and we simply wish to quickly retrieve the object.

    The nice thing about this implementation is that once you write data to
    disk, you *never* move it again. This also has an intersting impact on
    distributed hashsets or hashmaps. Once you place a value on a node,
    you never need to move that data again, which means you can resize your
    set or map without moving any data across the network.

    >>> from Persistent import Data, IntegerProperty
    >>> class Integer(Data):
    ...   value = IntegerProperty()
    ...
    >>> a = Hashset(Integer, "set_doctest.db")
    >>> ints = [Integer(value=i) for i in xrange(10000)]
    >>> for i in ints:
    ...   a.add(i)
    >>> [False for i in ints if not i in a]
    []

    >>> import os
    >>> os.remove("set_doctest.db")

    """

    fixed_collection = FixedSet

    def add(self, data):
        """ Adds an item to the set. """
        #TODO For data objects with only one property, allow setting like:
        # a.add("Steve")
        if self.collections[-1].set(data) == True:
            return
        self._add_collection()
        self.add(data)

    def get(self, data, default=None):
        """ Retrieves an item from the set.
        If the item doesn't exist, default is returned.

        """
        for fixed_set in reversed(self.collections):
            result = fixed_set.get(data)
            if result != None:
                return result
        return default

    def __contains__(self, data):
        """ Returns whether or not data is in the set. """
        return self.get(data) != None
