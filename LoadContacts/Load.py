import sys
sys.path.append("..")
from Contact.Contact import *
from Error.Error import *

class LoadContacts:

    def __init__(self, filepath):

        try:
            f = open(filepath, "r")
        except OSError:
            print("Could not open/read file:", filepath)
            sys.exit()

        try:
            # nombre de préhensions
            self.nb_contacts = int(f.readline().strip())
        except ValueError:
            # Handle the exception
            print("Wrong Format: line 1")
            sys.exit()

        try:
            # centre de masse de l'objet
            self.center_masse = list(map(float, f.readline().strip().split()))
            if len(self.center_masse) != 3:
                raise InputFormatError()
        except:
            # Handle the exception
            print("Wrong Format!")
            sys.exit()

        # list de préhensions
        self.contacts = []
        for i in range(self.nb_contacts):
            try:
                list_xyz = list(map(float, f.readline().strip().split()))
                if len(list_xyz) != 6:
                    raise InputFormatError()
            except:
                # Handle the exception
                print("Wrong Format!")
                sys.exit()
            point1 = list_xyz[:3]
            point2 = list_xyz[3:]
            self.contacts.append(Contact(point1, point2, self.center_masse))
        f.close()