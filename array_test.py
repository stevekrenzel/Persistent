def main():
    import os
    from random import randint
    from time import time
    from Persistent import Array

    filename = "vector_test.db"
    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        open(filename, 'w').close()

    db     = open(filename, "r+b")
    format = "I:age"
    size   = 100
    num    = 20000
    vector = Array(format, db)
    nums   = [randint(0, 100) for i in xrange(num)]

    t = time()
    for i, e in enumerate(nums):
        vector[i]["age"] = e
    print time() - t

    t = time()
    for i, e in enumerate(nums):
        if vector[i]["age"] != e:
            print "Shit"
    print time() - t

    db.close()
    db     = open(filename, "r+b")
    vector = Array(format, db, address=0)
    t = time()
    for i, e in enumerate(nums):
        if vector[i]["age"] != e:
            print "Shit"
    print time() - t
    db.close()
    os.remove(filename)

if __name__ == "__main__":
    main()
