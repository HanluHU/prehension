import unittest
from LoadFile.Load import *


class TestLoadFile(unittest.TestCase):
    """Test Load.py"""

    def test_init(self):
        """Test method __init__(self, file_path)"""
        data = LoadFile("../Data/test.txt")
        self.assertEqual(2, data.nb_grasps)
        self.assertEqual([2, 2, 2], data.center_masse)
        self.assertEqual(2, len(data.list_grasps))


if __name__ == '__main__':
    unittest.main(verbosity=2)
