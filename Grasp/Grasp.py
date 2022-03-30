import numpy as np
np.seterr(all='raise')


class Grasp:
    """Class for calculating the quality metrics of a grasp

        :param ndarray point_1: contact point 1
        :param ndarray point_2: contact point 2
        :param ndarray center_masse: center masse of the object to grasp
        :param ndarray __single_values: the single values of the grasp matrix
    """

    # point -> [x, y ,z]
    # grasp -> [point_1, point_2, center_masse]
    def __init__(self, point_1, point_2, center_masse):
        """Default constructor of the class Grasp, convert the input list object to Numpy array

            :param ndarray point_1: contact point 1
            :param ndarray point_2: contact point 2
            :param ndarray center_masse: center masse of the object to grasp

            :returns: a Grasp Object
            :rtype: Grasp
        """

        self.point_1 = np.array(point_1)
        self.point_2 = np.array(point_2)
        self.center_masse = np.array(center_masse)
        self.__single_values = np.array([])

    def calculate_n(self):
        """Calculate the vector n by calculating the vector from point_1 to point_2 and from point2 to point1

            :returns: the corresponding vector n of point_1 and point_2
            :rtype: ndarray
        """

        return self.point_2 - self.point_1, self.point_1 - self.point_2

    def calculate_o_t(self, point, n):
        """Calculate a random set of vector o and vector t with the point and its vector n

            The three vector n, t, o is perpendicular to each other.

            if we have the normal vector n = [A, B, C], the point P = [px, py, pz]

            point T and O are in the plane: Ax + By + Cz + D = 0, with D = -A*px -B*py -C*pz

            the vector P,T are perpendicular to the vector PO:

            (tx - px)(ox - px) + (ty - py)(oy - py) + (tz - pz)(oz - pz) = 0

            Atx + Bty + Ctz + D = 0

            Aox + Boy + Coz + D = 0

            3 equations, 6 variables ===> illimited solutions

            ox, oy = random integer ===> oz ===> point O

            tx = random integer ===> 3 equations, 3 variables ===> point T

            vector o = vector PO, vector t = vector PT

            :param ndarray point: contact point
            :param ndarray n: the vector n of the contact point in this Grasp

            :returns: the vector o and vector t of the contact point with the vector n
            :rtype: ndarray

            :raises ZeroDivisionError: a number is divided by a zero
        """

        # randomly define ox and oy, we can calculate oz
        ox = np.random.randint(50)
        while ox == point[0]:
            ox = np.random.randint(50)
        oy = np.random.randint(50)
        while oy == point[1]:
            oy = np.random.randint(50)
        try:
            # exception: division by zero
            oz = ((n * point).sum() - n[0] * ox - n[1] * oy) / n[2]
        except:
            oy = np.random.randint(50)
            while oy == point[1]:
                oy = np.random.randint(50)
            oz = np.random.randint(50)
            while oz == point[2]:
                oz = np.random.randint(50)
            try:
                ox = ((n * point).sum() - n[1] * oy - n[2] * oz) / n[0]
            except:
                ox = np.random.randint(50)
                while ox == point[0]:
                    ox = np.random.randint(50)
                oz = np.random.randint(50)
                while oz == point[2]:
                    oz = np.random.randint(50)
                oy = ((n * point).sum() - n[0] * ox - n[2] * oz) / n[1]
        # vector o = point_o - point
        o = np.array([ox - point[0], oy - point[1], oz - point[2]])

        # randomly define tx, we can build a linear system with 3 equations, 3 variables
        random_tx = np.random.randint(50)
        while random_tx == point[0] or random_tx == ox:
            random_tx = np.random.randint(50)
        a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [1, 0, 0]])
        b = np.array(
            [(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), random_tx])
        try:
            # exception: the determinant of the matrix a = 0
            t = np.linalg.solve(a, b)
        except:
            random_ty = np.random.randint(50)
            while random_ty == point[1] or random_ty == oy:
                random_ty = np.random.randint(50)
            a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [0, 1, 0]])
            b = np.array(
                [(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), random_ty])
            try:
                t = np.linalg.solve(a, b)
            except:
                random_tz = np.random.randint(50)
                while random_tz == point[2] or random_tz == oz:
                    random_tz = np.random.randint(50)
                a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [0, 0, 1]])
                b = np.array(
                    [(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), random_tz])
                t = np.linalg.solve(a, b)
        t = t - point

        # verify the direction of the vector t
        # cross_product(a, b) = norm(a) * norm(b) * sin(theta) * vector_n
        # sin(theta) = 1 or -1
        n = n/np.linalg.norm(n)
        cross_product_ot = np.cross(o, t)/(np.linalg.norm(o) * np.linalg.norm(t))
        # if sin(theta) == 1, wrong direction of the vector t
        if np.array_equal(cross_product_ot, n):
            return o, -t
        else:
            return o, t

    def calculate_rotation_matrix(self):
        """Calculate the rotation matrix of the two contact points

            First, normalize the vectors n, t, o. Then calculate the rotation matrix.

            rotation matrix = [n.T, t.T, o.T]

            :returns: 2 rotation matrix
            :rtype: ndarray
        """

        n_1, n_2 = self.calculate_n()
        o_1, t_1 = self.calculate_o_t(self.point_1, n_1)
        o_2, t_2 = self.calculate_o_t(self.point_2, n_2)
        r_1 = np.column_stack((n_1/np.linalg.norm(n_1), t_1/np.linalg.norm(t_1), o_1/np.linalg.norm(o_1)))
        r_2 = np.column_stack((n_2/np.linalg.norm(n_2), t_2/np.linalg.norm(t_2), o_2/np.linalg.norm(o_2)))
        return r_1, r_2

    def calculate_s_matrix(self, point):
        """Calculate the S Matrix of a contact point

            r = point - center_masse

            S(r) =

                    [ 0 , -rz,  ry]

                    [ rz,   0, -rx]

                    [-ry,  rx,   0]

            :param ndarray point: contact point

            :returns: the S matrix of the contact point
            :rtype: ndarray
        """

        vector = point - self.center_masse
        column_0 = np.array([0, vector[2], -vector[1]])
        column_1 = np.array([-vector[2], 0, vector[0]])
        column_2 = np.array([vector[1], -vector[0], 0])
        s = np.column_stack((column_0, column_1, column_2))
        return s

    def calculate_grasp_matrix(self):
        """Calculate the Grasp Matrix

            G(point) =

            [R(point), 0]

            [S(point - cm) * R(point), R(point)]

            G = [G(point1), G(point2)]

            :returns: the Grasp matrix of the current grasp
            :rtype: ndarray
        """

        r_1, r_2 = self.calculate_rotation_matrix()
        s_1 = self.calculate_s_matrix(self.point_1)
        s_2 = self.calculate_s_matrix(self.point_2)
        g_1 = np.vstack((np.hstack((r_1, np.zeros((3, 3)))), np.hstack((np.dot(s_1, r_1), r_1))))
        g_2 = np.vstack((np.hstack((r_2, np.zeros((3, 3)))), np.hstack((np.dot(s_2, r_2), r_2))))
        g = np.hstack((g_1, g_2))
        return g

    def calculate_grasp_matrix_single_values(self):
        """Calculate the single values of the Grasp Matrix

            stock the results in the attribut self.__single_values

            :returns: the single values of the Grasp Matrix
            :rtype: ndarray
        """

        g = self.calculate_grasp_matrix()
        u, s, vh = np.linalg.svd(g, full_matrices=True)
        self.__single_values = s
        return s

    def calculate_Q_MVS(self):
        """Calculate the quality metric Q_MVS

            Q_MVS = the minimum of the single values

            :returns: the quality metric Q_MVS
            :rtype: float
        """

        if self.__single_values.size == 0:
            self.calculate_grasp_matrix_single_values()
        return self.__single_values.min()

    def calculate_Q_VEM(self):
        """Calculate the quality metric Q_VEM

            Q_VEM = s1*s2*s3...*sn

            :returns: the quality metric Q_VEM
            :rtype: float
        """

        if self.__single_values.size == 0:
            self.calculate_grasp_matrix_single_values()
        return np.prod(self.__single_values)

    def calculate_Q_IIP(self):
        """Calculate the quality metric Q_IIP

            Q_IIP = min(s)/max(s)

            :returns: the quality metric Q_IIP
            :rtype: float
        """

        if self.__single_values.size == 0:
            self.calculate_grasp_matrix_single_values()
        return self.__single_values.min()/self.__single_values.max()
    def calculate_Q_DCC(self):
        """Calculate the quality metric Q_DCC

            Q_DCC = the distance between the center of the vector P1P2 and the center masse of the object

            :returns: the quality metric Q_DCC
            :rtype: float
        """

        center = (self.point_1 + self.point_2) / 2
        return np.linalg.norm(center - self.center_masse)
