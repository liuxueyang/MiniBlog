import unittest
from app.models import User, Permission, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.veriy_password('cat'))
        self.assertFalse(u.veriy_password('tac'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u1 = User(password='cat')
        self.assertTrue(u.password_hash != u1.password_hash)

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='liu_x@163.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
