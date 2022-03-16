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
        if n[2] == 0:
            if n[1] != 0:
                ox = np.random.randint(50)
                while ox == point[0]:
                    ox = np.random.randint(50)
                oz = np.random.randint(50)
                while oz == point[2]:
                    oz = np.random.randint(50)
                oy = ((n * point).sum() - n[0] * ox - n[2] * oz) / n[1]
                o = np.array([ox - point[0], oy - point[1], oz - point[2]])
            else:
                oy = np.random.randint(50)
                while oy == point[1]:
                    oy = np.random.randint(50)
                oz = np.random.randint(50)
                while oz == point[2]:
                    oz = np.random.randint(50)
                ox = ((n * point).sum() - n[1] * oy - n[2] * oz) / n[0]
                o = np.array([ox - point[0], oy - point[1], oz - point[2]])
        else:
            ox = np.random.randint(50)
            while ox == point[0]:
                ox = np.random.randint(50)
            oy = np.random.randint(50)
            while oy == point[1]:
                oy = np.random.randint(50)
            oz = ((n * point).sum() - n[0] * ox - n[1] * oy) / n[2]
            o = np.array([ox - point[0], oy - point[1], oz - point[2]])

        rand_tx = np.random.randint(50)
        while rand_tx == point[0] or rand_tx == ox:
            rand_tx = np.random.randint(50)
        linear_model = np.array([[n[0], n[1], n[2]],[ox-point[0], oy-point[1], oz-point[2]],[1, 0, 0]])
        if np.linalg.det(linear_model) == 0:
            rand_ty = np.random.randint(50)
            while rand_ty == point[1] or rand_ty == oy:
                rand_ty = np.random.randint(50)
            linear_model = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [0, 1, 0]])
            if np.linalg.det(linear_model) == 0:
                rand_tz = np.random.randint(50)
                while rand_tz == point[2] or rand_tz == oz:
                    rand_tz = np.random.randint(50)
                a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [0, 0, 1]])
                b = np.array([(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), rand_tz])
                t = np.linalg.solve(a, b)
                t = t - point
            else:
                a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [0, 1, 0]])
                b = np.array([(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), rand_ty])
                t = np.linalg.solve(a, b)
                t = t - point
        else:
            a = np.array([[n[0], n[1], n[2]],[ox-point[0], oy-point[1], oz-point[2]],[1, 0, 0]])
            b = np.array([(n * point).sum(), ox*point[0]+oy*point[1]+oz*point[2]-(point*point).sum(), rand_tx])
            t = np.linalg.solve(a, b)
            t = t - point

        n = n/np.linalg.norm(n)
        cross_product_ot = np.cross(o, t)/(np.linalg.norm(o) * np.linalg.norm(t))
        if np.array_equal(cross_product_ot, n):
            return o, -t
        else:
            return o, t

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