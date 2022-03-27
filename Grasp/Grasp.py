import numpy as np
np.seterr(all='raise')


class Grasp:

    # point -> [x, y ,z]
    # grasp -> [point_1, point_2, center_masse]
    def __init__(self, point_1, point_2, center_masse):

        self.point_1 = np.array(point_1)
        self.point_2 = np.array(point_2)
        self.center_masse = np.array(center_masse)
        self.__single_values = np.array([])

    # calculer vecteur n
    def calculate_n(self):

        return self.point_2 - self.point_1, self.point_1 - self.point_2

    # calculer vecteur o et t
    # si on a le vecteur normal n = [A, B, C], le point P = [px, py, pz]
    # point T et O sont dans le plan : Ax + By + Cz + D = 0, avec D = -A*px -B*py -C*pz
    # le vecteur PT est orthonormal au vecteur PO :
    # (tx - px)(ox - px) + (ty - py)(oy - py) + (tz - pz)(oz - pz) = 0
    #                                          Atx + Bty + Ctz + D = 0
    #                                          Aox + Boy + Coz + D = 0
    # 3 équations, 6 variables ===> solutions illimités
    # ox, oy = entier aléatoire ===> oz ===> point O
    # tx = entier aléatoire ===> 3 équations, 3 variables ===> point T
    # vecteur o = vecteur PO, vecteur t = vecteur PT
    def calculate_o_t(self, point, n):

        # définir ox et oy aléatoirement, on peut calculer oz
        ox = np.random.randint(50)
        while ox == point[0]:
            ox = np.random.randint(50)
        oy = np.random.randint(50)
        while oy == point[1]:
            oy = np.random.randint(50)
        try:
            # exception: division par zéro
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
        # vecteur o = point_o - point
        o = np.array([ox - point[0], oy - point[1], oz - point[2]])

        # définir tx aléatoirement, on peut établir un système linéaire avec 3 équations, 3 variables
        random_tx = np.random.randint(50)
        while random_tx == point[0] or random_tx == ox:
            random_tx = np.random.randint(50)
        a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [1, 0, 0]])
        b = np.array(
            [(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), random_tx])
        try:
            # exception: le déterminant de la matrice a = 0
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

        # vérifier la direction du vecteur t
        # cross_product(a, b) = norm(a)*norm(b)*sin(theta)*vecteur_n
        # sin(theta) = 1 ou -1
        n = n/np.linalg.norm(n)
        cross_product_ot = np.cross(o, t)/(np.linalg.norm(o) * np.linalg.norm(t))
        # si sin(theta) == 1, fausse direction du vecteur t
        if np.array_equal(cross_product_ot, n):
            return o, -t
        else:
            return o, t

    # matrice de rotation = [n.T, t.T, o.T]
    def calculate_rotation_matrix(self):

        n_1, n_2 = self.calculate_n()
        o_1, t_1 = self.calculate_o_t(self.point_1, n_1)
        o_2, t_2 = self.calculate_o_t(self.point_2, n_2)
        r_1 = np.column_stack((n_1/np.linalg.norm(n_1), t_1/np.linalg.norm(t_1), o_1/np.linalg.norm(o_1)))
        r_2 = np.column_stack((n_2/np.linalg.norm(n_2), t_2/np.linalg.norm(t_2), o_2/np.linalg.norm(o_2)))
        return r_1, r_2

    # S(r) = [ 0 , -rz,  ry]
    #        [ rz,   0, -rx]
    #        [-ry,  rx,   0]
    def calculate_s_matrix(self, point):

        vector = point - self.center_masse
        column_0 = np.array([0, vector[2], -vector[1]])
        column_1 = np.array([-vector[2], 0, vector[0]])
        column_2 = np.array([vector[1], -vector[0], 0])
        s = np.column_stack((column_0, column_1, column_2))
        return s

    # matrice de préhension G(point) = [                R(point),        0]
    #                                  [S(point - cm) * R(point), R(point)]
    #                              G = [G(point1), G(point2)]
    def calculate_grasp_matrix(self):

        r_1, r_2 = self.calculate_rotation_matrix()
        s_1 = self.calculate_s_matrix(self.point_1)
        s_2 = self.calculate_s_matrix(self.point_2)
        g_1 = np.vstack((np.hstack((r_1, np.zeros((3, 3)))), np.hstack((np.dot(s_1, r_1), r_1))))
        g_2 = np.vstack((np.hstack((r_2, np.zeros((3, 3)))), np.hstack((np.dot(s_2, r_2), r_2))))
        g = np.hstack((g_1, g_2))
        return g

    # calculer les valeurs singulières de la matrice de préhension G
    def calculate_grasp_matrix_single_values(self):

        g = self.calculate_grasp_matrix()
        u, s, vh = np.linalg.svd(g, full_matrices=True)
        self.__single_values = s

    # Q_MVS = le minimum des valeurs singulières
    def calculate_Q_MVS(self):

        if self.__single_values.size == 0:
            self.calculate_grasp_matrix_single_values()
        return self.__single_values.min()

    # Q_VEM = s1*s2*s3...*sn
    def calculate_Q_VEM(self):

        if self.__single_values.size == 0:
            self.calculate_grasp_matrix_single_values()
        return np.prod(self.__single_values)

    # Q_IIP = min(s)/max(s)
    def calculate_Q_IIP(self):

        if self.__single_values.size == 0:
            self.calculate_grasp_matrix_single_values()
        return self.__single_values.min()/self.__single_values.max()

    # Q_DCC = la distance entre le centre du vecteur P1P2 et le centre de masse de l'objet
    def calculate_Q_DCC(self):

        center = (self.point_1 + self.point_2) / 2
        return np.linalg.norm(center - self.center_masse)
