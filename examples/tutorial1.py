import os
from Persistent import Hashmap, Data, IntegerProperty, StringProperty

class PhoneEntry(Data):
    name    = StringProperty(10, key=True)
    phone   = IntegerProperty()

phonebook = Hashmap(PhoneEntry, 'phonebook.db')

phonebook.set(PhoneEntry(name="Steve", phone=6541234))
phonebook.set(PhoneEntry(name="Bob", phone=100100100))

print phonebook.get(PhoneEntry(name="Steve"))
print phonebook.get(PhoneEntry(name="Bob"))

phonebook.close()
os.remove('phonebook.db')
