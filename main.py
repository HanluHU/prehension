from LoadContacts.Load import *

data = LoadContacts("data.txt")

#print(data.nb_contacts)
#print(data.center_masse)
res = []
for i in data.contacts:
    print(i.point1, i.point2)
    res.append([i.get_Q_MVS(), i.get_Q_VEM(), i.get_Q_IIP(), i.get_Q_DCC()])
for i in res:
    print(i)