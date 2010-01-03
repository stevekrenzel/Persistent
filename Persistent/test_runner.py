import unittest
import doctest

suite = unittest.TestSuite()
for mod in ("Persistent.Property.property",
            "Persistent.Property.integer" ,
            "Persistent.Property.string"  ,
            "Persistent.Array.fixed_array",
            "Persistent.Array.array",
            "Persistent.Data.data"        ):
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner()
runner.run(suite)

