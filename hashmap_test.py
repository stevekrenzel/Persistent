def main():
    import os
    from Persistent import Hashmap, Data
    from time import time

    filename = "hashmap_test.db"

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()
    db = open(filename, "r+b")

    hashmap  = Hashmap("I:age", "20p:name", db)
    n = 40000

    k = Data("I:age")
    v = Data("20p:name")

    t = time()
    for i in xrange(n):
        k["age"] = i
        v["name"] = str(i)
        hashmap.set(k, v)
    print time() - t

    t = time()
    for i in xrange(n):
        k["age"] = i
        hashmap.get(k)
    print time() - t

    db.close()
    os.remove(filename)

if __name__ == "__main__":
    main()
