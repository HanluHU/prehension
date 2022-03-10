class Contact:

    # point -> [x, y ,z]
    # contact -> [point1, point2]
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def calculate_n(self):
        n1 = []
        n2 = []
        for i in range(3):
            n1.append(self.point2[i] - self.point1[i])
            n2.append(self.point1[i] - self.point2[i])
        return n1, n2

    def calculate_ot(self, point, n):
        if n[0] == n[1] == 0:
            if n[2] > 0:
                return [0, 1, 0], [1, 0, 0]
            else:
                return [0, 1, 0], [-1, 0, 0]
        if n[0] == n[2] == 0:
            if n[1] > 0:
                return [0, 0, 1], [-1, 0, 0]
            else:
                return [0, 0, 1], [1, 0, 0]
        if n[1] == n[2] == 0:
            if n[0] > 0:
                return [0, 0, 1], [0, 1, 0]
            else:
                return [0, 0, 1], [0, -1, 0]

        ox = 1 + point[0]
        oy = 1 + point[1]
        oz = point[2] - (n[0] + n[1])/n[2]
        tz = 1 + point[2]
        ty = (-n[2] + (n[1]-n[0])*point[1] - (n[0]*(n[0]+n[1]))/n[2]) / (n[1]-n[0])
        tx = point[0] + point[1] + (n[0]+n[1])/n[2] - ty
        o1 = [ox - point[0], oy - point[1], oz - point[2]]
        t1 = [tx - point[0], ty - point[1], tz - point[2]]
        if n[0] < 0:
            return o1, t1
        else:
            return [-i for i in o1], t1

    def calculate_rotation_matrix(self):
        n1, n2 = self.calculate_n()
        o1, t1 = self.calculate_ot(self.point1, n1)
        o2, t2 = self.calculate_ot(self.point2, n2)
        return [n1, t1, o1], [n2, t2, o2]