from Persistent import Hashmap
from Persistent.Data.test import Data
from Persistent.Data.property import IntegerProperty

class PhoneEntry(Data):
    name  = IntegerProperty(key=True)
    phone = IntegerProperty()

phonebook = Hashmap(PhoneEntry, 'phonebook.db')

phonebook.set(PhoneEntry(name=123, phone=456))
phonebook.set(PhoneEntry(name=789, phone=101))

print phonebook.get(PhoneEntry(name=123))
print phonebook.get(PhoneEntry(name=789))

phonebook.close()

