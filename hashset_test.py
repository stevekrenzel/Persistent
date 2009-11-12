def main():
    import os
    from random import randint, seed
    from Persistent import Hashset, Data
    from time import time
    seed(6)

    filename = "hashset_test.db"
    rands    = set([randint(0, 50000000) for i in xrange(25000)])
    data    = []
    format   = "I:age, 20p:name"
    for r in rands:
        d = Data(format)
        d["age"]  = r
        d["name"] = "Steve"
        data.append(d)
    del(rands)

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()
    db = open(filename, "r+b")

    hashset  = Hashset(format, db)

    t = time()
    for d in data:
        hashset.set(d)
    print time() - t

    t = time()
    for d in data:
        if hashset.get(d) != d:
            print "SHIT"
    print time() - t

    db.close()
    os.remove(filename)

if __name__ == "__main__":
    main()

