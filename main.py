from LoadContacts.Load import *

data = LoadContacts("test.txt")

print(data.nb_contacts)
for i in data.contacts:
    print(i.point1, i.point2)
    print(i.calculate_rotation_matrix())