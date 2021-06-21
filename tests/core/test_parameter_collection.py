import unittest

from pydidas.core import  Parameter, ParameterCollection


class TestParameterCollection(unittest.TestCase):

    def setUp(self):
        self._params = [Parameter('Test0', int, default=12),
                        Parameter('Test1', str, default='test str'),
                        Parameter('Test2', int, default=3),
                        Parameter('Test3', float, default=12)]

    def tearDown(self):
        ...

    def test_creation(self):
        obj = ParameterCollection()
        self.assertIsInstance(obj, ParameterCollection)

    def test_creation_with_args(self):
        obj = ParameterCollection(*self._params)
        for index in range(4):
            self.assertEqual(obj[f'Test{index}'],
                             self._params[index])

    def test_creation_params_with_kwargs(self):
        obj = ParameterCollection(Test0=self._params[0],
                                  Test1=self._params[1],
                                  Test2=self._params[2],
                                  Test3=self._params[3],
                                  )
        for index in range(4):
            self.assertEqual(obj[f'Test{index}'],
                             self._params[index])

    def test_add_params_with_args(self):
        obj = ParameterCollection(*self._params)
        obj.add_params(Parameter('Test5', int, default=12),
                       Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                 Parameter)

    def test_add_params_with_kwargs(self):
        obj = ParameterCollection(*self._params)
        obj.add_params(Test5=Parameter('Test5', int, default=12),
                       Test6=Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                 Parameter)

    def test_add_params_mixed(self):
        obj = ParameterCollection(*self._params)
        obj.add_params(Parameter('Test5', int, default=12),
                       Test6=Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                 Parameter)

    def test_add_params_collection(self):
        obj = ParameterCollection(*self._params)
        coll = ParameterCollection(Parameter('Test7', str, default='Test'),
                                   Parameter('Test8', float, default=0))
        obj.add_params(Parameter('Test5', int, default=12),
                       coll,
                       Test6=Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                 Parameter)

    def test_add_params_duplicate(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.add_params(Parameter('Test5', float, default=-1),
                           Test5=Parameter('Test5', int, default=12))
        with self.assertRaises(KeyError):
            obj.add_params(Parameter('Test5', float, default=-1),
                           Parameter('Test5', int, default=12))

    def test_get_copy(self):
        obj = ParameterCollection(*self._params)
        _copy = obj.get_copy()
        self.assertNotEqual(obj, _copy)

    def test_get_value(self):
        obj = ParameterCollection(*self._params)
        self.assertEqual(12, obj.get_value('Test0'))
        with self.assertRaises(KeyError):
            obj.get_value('TEST')

    def test_set_item(self):
        obj = ParameterCollection(*self._params)
        obj['Test5'] = Parameter('Test5', float, default=-1)
        with self.assertRaises(TypeError):
            obj['Test6'] = 12
        with self.assertRaises(KeyError):
            obj['Test6'] = Parameter('Test5', float, default=-1)

    def test_delete_param(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.delete_param('TEST')
        obj.delete_param('Test0')
        self.assertNotIn('Test0', obj.keys())

    def test_set_value(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.set_value('Test6', 12)
        obj.set_value('Test0', 0)
        self.assertEqual(obj.get_value('Test0'), 0)

if __name__ == "__main__":
    unittest.main()
