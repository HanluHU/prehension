import unittest
import numpy as np
from Grasp.Grasp import *


class TestGrasp(unittest.TestCase):
    """Test Grasp.py"""

    def test_init(self):
        """Test method __init__(self, point_1, point_2, center_masse)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])

        self.assertEqual(np.__name__, type(grasp.point_1).__module__)
        self.assertEqual(4, grasp.point_1[0])
        self.assertEqual(1, grasp.point_1[1])
        self.assertEqual(1, grasp.point_1[2])

        self.assertEqual(np.__name__, type(grasp.point_2).__module__)
        self.assertEqual(0, grasp.point_2[0])
        self.assertEqual(1, grasp.point_2[1])
        self.assertEqual(1, grasp.point_2[2])

        self.assertEqual(np.__name__, type(grasp.center_masse).__module__)
        self.assertEqual(2, grasp.center_masse[0])
        self.assertEqual(2, grasp.center_masse[1])
        self.assertEqual(2, grasp.center_masse[2])

    def test_calculate_n(self):
        """Test method calculate_n(self)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        n_1, n_2 = grasp.calculate_n()

        self.assertEqual(np.__name__, type(n_1).__module__)
        self.assertEqual(-4, n_1[0])
        self.assertEqual(0, n_1[1])
        self.assertEqual(0, n_1[2])

        self.assertEqual(np.__name__, type(n_2).__module__)
        self.assertEqual(4, n_2[0])
        self.assertEqual(0, n_2[1])
        self.assertEqual(0, n_2[2])

    def test_calculate_o_t(self):
        """Test method calculate_o_t(self, point, n)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        n_1, n_2 = grasp.calculate_n()
        o_1, t_1 = grasp.calculate_o_t(grasp.point_1, n_1)
        o_2, t_2 = grasp.calculate_o_t(grasp.point_2, n_2)

        self.assertEqual(True, (n_1 * o_1).sum() < 0.001)
        self.assertEqual(True, (n_1 * t_1).sum() < 0.001)
        self.assertEqual(True, (t_1 * o_1).sum() < 0.001)

        n_1 = n_1 / np.linalg.norm(n_1)
        cross_product_ot_1 = np.cross(o_1, t_1) / (np.linalg.norm(o_1) * np.linalg.norm(t_1))
        self.assertEqual(False, np.array_equal(cross_product_ot_1, n_1))
        n_2 = n_2 / np.linalg.norm(n_2)
        cross_product_ot_2 = np.cross(o_2, t_2) / (np.linalg.norm(o_2) * np.linalg.norm(t_2))
        self.assertEqual(False, np.array_equal(cross_product_ot_2, n_2))

    def test_calculate_rotation_matrix(self):
        """Test method calculate_rotation_matrix(self)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        r_1, r_2 = grasp.calculate_rotation_matrix()
        n_1 = r_1[:, 0]
        t_1 = r_1[:, 1]
        o_1 = r_1[:, 2]
        n_2 = r_2[:, 0]
        t_2 = r_2[:, 1]
        o_2 = r_2[:, 2]

        self.assertEqual(True, (n_1 * o_1).sum() < 0.001)
        self.assertEqual(True, (n_1 * t_1).sum() < 0.001)
        self.assertEqual(True, (t_1 * o_1).sum() < 0.001)

        n_1 = n_1 / np.linalg.norm(n_1)
        cross_product_ot_1 = np.cross(o_1, t_1) / (np.linalg.norm(o_1) * np.linalg.norm(t_1))
        self.assertEqual(False, np.array_equal(cross_product_ot_1, n_1))
        n_2 = n_2 / np.linalg.norm(n_2)
        cross_product_ot_2 = np.cross(o_2, t_2) / (np.linalg.norm(o_2) * np.linalg.norm(t_2))
        self.assertEqual(False, np.array_equal(cross_product_ot_2, n_2))

    def test_calculate_s_matrix(self):
        """Test method calculate_s_matrix(self, point)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        s_1 = grasp.calculate_s_matrix(grasp.point_1)
        vector = grasp.point_1 - grasp.center_masse

        self.assertEqual(True, np.array_equal(np.array([0, vector[2], -vector[1]]), s_1[:, 0]))
        self.assertEqual(True, np.array_equal(np.array([-vector[2], 0, vector[0]]), s_1[:, 1]))
        self.assertEqual(True, np.array_equal(np.array([vector[1], -vector[0], 0]), s_1[:, 2]))

    def test_calculate_grasp_matrix(self):
        """Test method calculate_grasp_matrix(self)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        g = grasp.calculate_grasp_matrix()
        g1 = g[:, :6]
        g2 = g[:, 6:]

        self.assertEqual(True, np.array_equal(np.zeros((3, 3)), g1[:3, 3:]))
        self.assertEqual(True, np.array_equal(np.zeros((3, 3)), g2[:3, 3:]))

    def test_calculate_Q_MVS(self):
        """Test method calculate_Q_MVS(self)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        s = grasp.calculate_grasp_matrix_single_values()

        self.assertEqual(s.min(), grasp.calculate_Q_MVS())

    def test_calculate_Q_VEM(self):
        """Test method calculate_Q_VEM(self)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        s = grasp.calculate_grasp_matrix_single_values()

        self.assertEqual(np.prod(s), grasp.calculate_Q_VEM())

    def test_calculate_Q_IIP(self):
        """Test method calculate_Q_IIP(self)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        s = grasp.calculate_grasp_matrix_single_values()

        self.assertEqual(s.min()/s.max(), grasp.calculate_Q_IIP())

    def test_calculate_Q_DCC(self):
        """Test method calculate_Q_DCC(self)"""
        grasp = Grasp([4, 1, 1], [0, 1, 1], [2, 2, 2])
        center = (grasp.point_1 + grasp.point_2) / 2
        distance = np.linalg.norm(center - grasp.center_masse)

        self.assertEqual(distance, grasp.calculate_Q_DCC())

if __name__ == '__main__':
    unittest.main(verbosity=2)
