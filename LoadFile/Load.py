import sys
sys.path.append("..")
from Grasp.Grasp import *
from Error.Error import *


class LoadFile:
    """Class for reading data from a file

        :param int nb_grasps: total number of grasps in the data file
        :param list center_masse: the center masse of the object to grasp
        :param list list_grasps: the list of all the Grasp objects
    """

    def __init__(self, file_path):
        """Default constructor of the class LoadFile

            :param str file_path: the path of the input data file

            :returns: a LoadFile Object that contains all the Grasp objects in the data file
            :rtype: LoadFile

            :raises OSError: Fail to open/read file
            :raises ValueError: Fail to transform string to int/float
            :raises InputFormatError: Wrong format of the file
        """


        # Open file and read
        file = open(file_path, "r")

        # Read the number of grasps in the file
        self.nb_grasps = int(file.readline().strip())

        # Read the center masse of the object
        self.center_masse = list(map(float, file.readline().strip().split()))
        if len(self.center_masse) != 3:
            raise InputFormatError()

        # list of grasps
        self.list_grasps = []
        for i in range(self.nb_grasps):
            # Read the two points in one row
            list_xyz = list(map(float, file.readline().strip().split()))
            if len(list_xyz) != 6:
                raise InputFormatError()
            point_1 = list_xyz[:3]
            point_2 = list_xyz[3:]
            # Add the Grasp to the list
            self.list_grasps.append(Grasp(point_1, point_2, self.center_masse))
        file.close()
