import sys
sys.path.append("..")
from Grasp.Grasp import *
from Error.Error import *


class LoadFile:

    def __init__(self, file_path):

        try:
            file = open(file_path, "r")
        except OSError:
            print("Could not open/read file:", file_path)
            sys.exit()

        try:
            # nombre de préhensions
            self.nb_grasps = int(file.readline().strip())
        except ValueError:
            # Handle the exception
            print("Wrong Format: line 1")
            sys.exit()

        try:
            # centre de masse de l'objet
            self.center_masse = list(map(float, file.readline().strip().split()))
            if len(self.center_masse) != 3:
                raise InputFormatError()
        except:
            # Handle the exception
            print("Wrong Format!")
            sys.exit()

        # list de préhensions
        self.list_grasps = []
        for i in range(self.nb_grasps):
            try:
                list_xyz = list(map(float, file.readline().strip().split()))
                if len(list_xyz) != 6:
                    raise InputFormatError()
            except:
                # Handle the exception
                print("Wrong Format!")
                sys.exit()
            point_1 = list_xyz[:3]
            point_2 = list_xyz[3:]
            self.list_grasps.append(Grasp(point_1, point_2, self.center_masse))
        file.close()
