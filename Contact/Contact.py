import numpy as np

class Contact:

    # point -> [x, y ,z]
    # contact -> [point1, point2]
    def __init__(self, point1, point2, cm):
        self.point1 = np.array(point1, dtype=np.float)
        self.point2 = np.array(point2, dtype=np.float)
        self.center_masse = np.array(cm, dtype=np.float)
        self.__s = np.array([])

    def calculate_n(self):
        return self.point2 - self.point1, self.point1 - self.point2

    def calculate_ot(self, point, n):
        if n[0] == n[1] == 0:
            if n[2] > 0:
                return np.array([0, 1, 0]), np.array([1, 0, 0])
            else:
                return np.array([0, 1, 0]), np.array([-1, 0, 0])
        if n[0] == n[2] == 0:
            if n[1] > 0:
                return np.array([0, 0, 1]), np.array([-1, 0, 0])
            else:
                return np.array([0, 0, 1]), np.array([1, 0, 0])
        if n[1] == n[2] == 0:
            if n[0] > 0:
                return np.array([0, 0, 1]), np.array([0, 1, 0])
            else:
                return np.array([0, 0, 1]), np.array([0, -1, 0])

        ox = 1 + point[0]
        oy = 1 + point[1]
        oz = point[2] - (n[0] + n[1])/n[2]
        tz = 1 + point[2]
        ty = (-n[2] + (n[1]-n[0])*point[1] - (n[0]*(n[0]+n[1]))/n[2]) / (n[1]-n[0])
        tx = point[0] + point[1] + (n[0]+n[1])/n[2] - ty
        o1 = np.array([ox - point[0], oy - point[1], oz - point[2]])
        t1 = np.array([tx - point[0], ty - point[1], tz - point[2]])
        if n[0] < 0:
            return o1, t1
        else:
            return -o1, t1

    def calculate_rotation_matrix(self):
        n1, n2 = self.calculate_n()
        o1, t1 = self.calculate_ot(self.point1, n1)
        o2, t2 = self.calculate_ot(self.point2, n2)
        R1 = np.column_stack((n1/np.linalg.norm(n1), t1/np.linalg.norm(t1), o1/np.linalg.norm(o1)))
        R2 = np.column_stack((n2/np.linalg.norm(n2), t2/np.linalg.norm(t2), o2/np.linalg.norm(o2)))
        return R1, R2

    def calculate_s_matrix(self, point):
        vector = point - self.center_masse
        col1 = np.array([0, vector[2], -vector[1]])
        col2 = np.array([-vector[2], 0, vector[0]])
        col3 = np.array([vector[1], -vector[0], 0])
        S = np.column_stack((col1, col2, col3))
        return S

    def calculate_grasp_matrix(self):
        R1, R2 = self.calculate_rotation_matrix()
        S1 = self.calculate_s_matrix(self.point1)
        S2 = self.calculate_s_matrix(self.point2)
        G1 = np.vstack((np.hstack((R1, np.zeros((3, 3)))), np.hstack((np.dot(S1, R1), R1))))
        G2 = np.vstack((np.hstack((R2, np.zeros((3, 3)))), np.hstack((np.dot(S2, R2), R2))))
        G = np.hstack((G1, G2))
        return G

    def grasp_matrix_svd(self):
        G = self.calculate_grasp_matrix()
        u, s, vh = np.linalg.svd(G, full_matrices=True)
        self.__s = s

    def get_Q_MVS(self):
        if self.__s.size == 0:
            self.grasp_matrix_svd()
        return self.__s.min()

    def get_Q_VEM(self):
        if self.__s.size == 0:
            self.grasp_matrix_svd()
        return np.prod(self.__s)

    def get_Q_IIP(self):
        if self.__s.size == 0:
            self.grasp_matrix_svd()
        return self.__s.min()/self.__s.max()

    def get_Q_DCC(self):
        c = (self.point1 + self.point2) / 2
        return np.linalg.norm(c - self.center_masse)