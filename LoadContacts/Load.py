import sys
sys.path.append("..")
from Contact.Contact import *

class LoadContacts:

    def __init__(self, filepath):
        f = open(filepath, "r")
        # nombre de préhensions
        self.nb_contacts = int(f.readline().strip())
        # centre de masse de l'objet
        self.center_masse = list(map(float, f.readline().strip().split()))
        # list de préhensions
        self.contacts = []
        for i in range(self.nb_contacts):
            list_xyz = list(map(float, f.readline().strip().split()))
            point1 = list_xyz[:3]
            point2 = list_xyz[3:]
            self.contacts.append(Contact(point1, point2, self.center_masse))
        f.close()