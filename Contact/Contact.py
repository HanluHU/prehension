import numpy as np
np.seterr(all='raise')

class Contact:

    # point -> [x, y ,z]
    # contact -> [point1, point2, cm]
    def __init__(self, point1, point2, cm):
        self.point1 = np.array(point1, dtype=np.float)
        self.point2 = np.array(point2, dtype=np.float)
        self.center_masse = np.array(cm, dtype=np.float)
        self.__s = np.array([])

    # calculer vecteur n
    def calculate_n(self):
        return self.point2 - self.point1, self.point1 - self.point2

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
    def calculate_ot(self, point, n):
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
        rand_tx = np.random.randint(50)
        while rand_tx == point[0] or rand_tx == ox:
            rand_tx = np.random.randint(50)
        a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [1, 0, 0]])
        b = np.array(
            [(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), rand_tx])
        try:
            # exception: le déterminant de la matrice a = 0
            t = np.linalg.solve(a, b)
        except:
            rand_ty = np.random.randint(50)
            while rand_ty == point[1] or rand_ty == oy:
                rand_ty = np.random.randint(50)
            a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [0, 1, 0]])
            b = np.array(
                [(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), rand_ty])
            try:
                t = np.linalg.solve(a, b)
            except:
                rand_tz = np.random.randint(50)
                while rand_tz == point[2] or rand_tz == oz:
                    rand_tz = np.random.randint(50)
                a = np.array([[n[0], n[1], n[2]], [ox - point[0], oy - point[1], oz - point[2]], [0, 0, 1]])
                b = np.array(
                    [(n * point).sum(), ox * point[0] + oy * point[1] + oz * point[2] - (point * point).sum(), rand_tz])
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
        n1, n2 = self.calculate_n()
        o1, t1 = self.calculate_ot(self.point1, n1)
        o2, t2 = self.calculate_ot(self.point2, n2)
        R1 = np.column_stack((n1/np.linalg.norm(n1), t1/np.linalg.norm(t1), o1/np.linalg.norm(o1)))
        R2 = np.column_stack((n2/np.linalg.norm(n2), t2/np.linalg.norm(t2), o2/np.linalg.norm(o2)))
        return R1, R2

    # S(r) = [ 0 , -rz,  ry]
    #        [ rz,   0, -rx]
    #        [-ry,  rx,   0]
    def calculate_s_matrix(self, point):
        vector = point - self.center_masse
        col1 = np.array([0, vector[2], -vector[1]])
        col2 = np.array([-vector[2], 0, vector[0]])
        col3 = np.array([vector[1], -vector[0], 0])
        S = np.column_stack((col1, col2, col3))
        return S

    # matrice de préhension G(point) = [                R(point),        0]
    #                                  [S(point - cm) * R(point), R(point)]
    #                              G = [G(point1), G(point2)]
    def calculate_grasp_matrix(self):
        R1, R2 = self.calculate_rotation_matrix()
        S1 = self.calculate_s_matrix(self.point1)
        S2 = self.calculate_s_matrix(self.point2)
        G1 = np.vstack((np.hstack((R1, np.zeros((3, 3)))), np.hstack((np.dot(S1, R1), R1))))
        G2 = np.vstack((np.hstack((R2, np.zeros((3, 3)))), np.hstack((np.dot(S2, R2), R2))))
        G = np.hstack((G1, G2))
        return G

    # calculer les valeurs singulières de la matrice de préhension G
    def grasp_matrix_svd(self):
        G = self.calculate_grasp_matrix()
        u, s, vh = np.linalg.svd(G, full_matrices=True)
        self.__s = s

    # Q_MVS = le minimum des valeurs singulières
    def get_Q_MVS(self):
        if self.__s.size == 0:
            self.grasp_matrix_svd()
        return self.__s.min()

    # Q_VEM = s1*s2*s3...*sn
    def get_Q_VEM(self):
        if self.__s.size == 0:
            self.grasp_matrix_svd()
        return np.prod(self.__s)

    # Q_IIP = min(s)/max(s)
    def get_Q_IIP(self):
        if self.__s.size == 0:
            self.grasp_matrix_svd()
        return self.__s.min()/self.__s.max()

    # Q_DCC = la distance entre le centre du vecteur P1P2 et le centre de masse de l'objet
    def get_Q_DCC(self):
        c = (self.point1 + self.point2) / 2
        return np.linalg.norm(c - self.center_masse)