import unittest
import time
import string
import random

from pydidas.core import SingletonFactory


class TestClass:
    def __init__(self):
        self.attr1 = hash(time.time())
        self.attr2 = ''.join(random.choice(string.ascii_letters)
                             for i in range(64))


class TestParameterCollection(unittest.TestCase):

    def setUp(self):
        self.factory = SingletonFactory(TestClass)

    def tearDown(self):
        ...

    def test_setup(self):
        # test setUp method
        self.assertIsInstance(self.factory, SingletonFactory)

    def test_creation(self):
        obj = self.factory()
        self.assertIsInstance(obj, TestClass)

    def test_repeated_call(self):
        obj = self.factory()
        obj2 = self.factory()
        self.assertEqual(obj, obj2)

    def test_instance(self):
        obj = self.factory.instance()
        self.assertIsInstance(obj, TestClass)

if __name__ == "__main__":
    unittest.main()
