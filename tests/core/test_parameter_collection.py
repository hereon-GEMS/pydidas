# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import copy

from pydidas.core import Parameter, ParameterCollection


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

    def test_add_params_with_kwarg_wrong_type(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(TypeError):
            obj.add_params(Test5=1)

    def test_add_params_mixed(self):
        obj = ParameterCollection(*self._params)
        obj.add_params(Parameter('Test5', int, default=12),
                       Test6=Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                 Parameter)

    def test_add_params__mixed_with_collection(self):
        obj = ParameterCollection(*self._params)
        coll = ParameterCollection(Parameter('Test7', str, default='Test'),
                                   Parameter('Test8', float, default=0))
        obj.add_params(Parameter('Test5', int, default=12),
                       coll,
                       Test6=Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                 Parameter)

    def test_add_params_collection(self):
        obj = ParameterCollection(*self._params)
        coll = ParameterCollection(Parameter('Test7', str, default='Test'),
                                   Parameter('Test8', float, default=0))
        obj.add_params(coll)
        for index in range(7, 9):
            self.assertIsInstance(obj[f'Test{index}'],
                                 Parameter)

    def test_add_arg_params__with_collection(self):
        obj = ParameterCollection(*self._params)
        coll = ParameterCollection(Parameter('Test7', str, default='Test'),
                                   Parameter('Test8', float, default=0))
        obj._ParameterCollection__add_arg_params(coll)
        for index in range(7, 9):
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

    def test_copy(self):
        obj = ParameterCollection(*self._params)
        _copy = copy.copy(obj)
        self.assertNotEqual(obj, _copy)
        self.assertIsInstance(_copy, ParameterCollection)

    def test__raise_type_error(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(TypeError):
            obj._ParameterCollection__raise_type_error('test')

    def test__add_arg_params_with_param_collection(self):
        obj = ParameterCollection(*self._params)
        obj2 = ParameterCollection()
        obj2._ParameterCollection__add_arg_params(obj)

    def test__check_arg_types(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(TypeError):
            obj._ParameterCollection__check_arg_types(*[0])

    def test__check_kwarg_types(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(TypeError):
            obj._ParameterCollection__check_kwarg_types({'test': 0})

    def test_get_param(self):
        obj = ParameterCollection(*self._params)
        _p = obj.get_param('Test0')
        self.assertIsInstance(_p, Parameter)

if __name__ == "__main__":
    unittest.main()
