import unittest
from .. app.model import User


class TestPasswordHashCase(unittest.TestCase):
    def setUp(self):
        self.u = User()

    def tearDown(self):
        pass

    def test_set_password(self):
        self.u.password = '123456'
        self.assertTrue(self.u.password_hash is not None)

    def test_direct_use_password(self):
        self.u.password = '123456'
        with self.assertRaises(AttributeError):
            self.u.password

    def test_random_password(self):
        u1 = User()
        u1.password = '123456'
        u2 = User()
        u2.password = '123456'
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_password_veri(self):
        self.u.password = '123456'
        self.assertTrue(self.u.verify_password('123456'))
        self.assertFalse(self.u.verify_password('654321'))
if __name__ == '__main__':
    unittest.main()
