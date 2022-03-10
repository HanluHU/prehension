import sys
sys.path.append("..")
from Contact.Contact import *

class LoadContacts:

    def __init__(self, filepath):
        f = open(filepath, "r")
        self.nb_contacts = int(f.readline().strip())
        self.contacts = []
        for i in range(self.nb_contacts):
            list_xyz = list(map(float, f.readline().strip().split()))
            point1 = list_xyz[:3]
            point2 = list_xyz[3:]
            self.contacts.append(Contact(point1, point2))