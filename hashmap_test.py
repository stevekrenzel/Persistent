def main():
    import os
    from random import randint, seed
    from Persistent import Hashmap, Data
    from time import time

    filename = "hashmap_test.db"

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()
    db = open(filename, "r+b")

    hashmap  = Hashmap("I:age", "20p:name", db)
    n = 200000

    k = Data("I:age")
    v = Data("20p:name")

    seed(6)
    t = time()
    for i in xrange(n):
        k["age"] = i
        v["name"] = str(randint(0, 50000000))
        hashmap.set(k, v)
    print time() - t

    seed(6)
    t = time()
    for i in xrange(n):
        k["age"] = i
        hashmap.get(k)
    print time() - t

    db.close()
    os.remove(filename)

if __name__ == "__main__":
    main()
