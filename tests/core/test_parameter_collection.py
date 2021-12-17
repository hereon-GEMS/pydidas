# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import copy

from pydidas.core import Parameter, ParameterCollection


class TestParameterCollection(unittest.TestCase):

    def setUp(self):
        self._params = [Parameter('Test0', int, 12),
                        Parameter('Test1', str, 'test str'),
                        Parameter('Test2', int, 3),
                        Parameter('Test3', float, 12)]

    def tearDown(self):
        ...

    def test_setup(self):
        # assert no Exception in setUp method.
        pass

    def test_get_param(self):
        obj = ParameterCollection(*self._params)
        _p = obj.get_param('Test0')
        self.assertIsInstance(_p, Parameter)

    def test_get_param__wrong_key(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.get_param('no such test')

    def test_get_params(self):
        obj = ParameterCollection(*self._params)
        _ps = obj.get_params('Test0', 'Test1')
        self.assertEqual(_ps, self._params[0:2])

    def test_get_params__wrong_key(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.get_params('Test0', 'Test1', 'no such test')

    def test_set_value(self):
        obj = ParameterCollection(*self._params)
        obj.set_value('Test0', 0)
        self.assertEqual(obj.get_value('Test0'), 0)

    def test_set_value__wrong_key(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.set_value('Test6', 12)

    def test_get_value(self):
        obj = ParameterCollection(*self._params)
        self.assertEqual(12, obj.get_value('Test0'))

    def test_get_value__wrong_key(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.get_value('TEST')

    def test_get_copy(self):
        obj = ParameterCollection(*self._params)
        _copy = copy.copy(obj)
        self.assertNotEqual(obj, _copy)
        self.assertIsInstance(_copy, ParameterCollection)

    def test_delete_param(self):
        obj = ParameterCollection(*self._params)
        obj.delete_param('Test0')
        self.assertNotIn('Test0', obj.keys())

    def test_delete_param__wrong_key(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.delete_param('TEST')

    def test_add_kwarg_params(self):
        obj = ParameterCollection()
        obj._ParameterCollection__add_kwarg_params(Test0=self._params[0],
                                                    Test1=self._params[1])
        self.assertEqual(obj.__getitem__('Test0'), self._params[0])
        self.assertEqual(obj.__getitem__('Test1'), self._params[1])

    def test_add_arg_params__with_param_collection(self):
        tester = ParameterCollection(*self._params)
        obj = ParameterCollection()
        obj._ParameterCollection__add_arg_params(tester)
        for item in self._params:
            self.assertTrue(item in obj.values())

    def test_add_arg_params__with_params(self):
        obj = ParameterCollection()
        obj._ParameterCollection__add_arg_params(*self._params)
        for item in self._params:
            self.assertTrue(item in obj.values())

    def test_add_arg_params__with_mixed_items(self):
        tester = ParameterCollection(*self._params[1:])
        obj = ParameterCollection()
        obj._ParameterCollection__add_arg_params(self._params[0], tester)
        for item in self._params:
            self.assertTrue(item in obj.values())

    def test_add_arg_params__with_collection(self):
        obj = ParameterCollection(*self._params)
        coll = ParameterCollection(Parameter('Test7', str, default='Test'),
                                    Parameter('Test8', float, default=0))
        obj._ParameterCollection__add_arg_params(coll)
        for index in range(7, 9):
            self.assertIsInstance(obj[f'Test{index}'],
                                  Parameter)

    def test_check_duplicate_keys__only_args(self):
        obj = ParameterCollection()
        obj._ParameterCollection__check_duplicate_keys(*self._params)
        # assert passes

    def test_check_duplicate_keys__only_args_with_duplicate(self):
        obj = ParameterCollection()
        self._params.append(Parameter('Test0', int, 42))
        with self.assertRaises(KeyError):
            obj._ParameterCollection__check_duplicate_keys(*self._params)

    def test_check_duplicate_keys__only_kwargs(self):
        obj = ParameterCollection()
        obj._ParameterCollection__check_duplicate_keys(
            Test0=self._params[0], Test1=self._params[1])
        # assert passes

    def test_check_duplicate_keys__mixed_no_duplicate(self):
        obj = ParameterCollection()
        obj._ParameterCollection__check_duplicate_keys(
            self._params[0], Test1=self._params[1])
        # assert passes

    def test_check_duplicate_keys__mixed_with_duplicate(self):
        obj = ParameterCollection()
        with self.assertRaises(KeyError):
            obj._ParameterCollection__check_duplicate_keys(
                self._params[0], Test0=Parameter('Test0', int, 42))

    def test_check_kwarg_types(self):
        obj = ParameterCollection()
        obj._ParameterCollection__check_kwarg_types(
            Test0=self._params[0], Test1=self._params[1])

    def test_check_kwarg_types__wrong_type(self):
        obj = ParameterCollection()
        with self.assertRaises(TypeError):
            obj._ParameterCollection__check_kwarg_types(dict(test=0))

    def test_add_params__with_args(self):
        obj = ParameterCollection(*self._params)
        obj.add_params(Parameter('Test5', int, default=12),
                        Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                  Parameter)

    def test_add_params__with_kwargs(self):
        obj = ParameterCollection(*self._params)
        obj.add_params(Test5=Parameter('Test5', int, default=12),
                        Test6=Parameter('Test6', float, default=-1),)
        for index in range(5,6):
            self.assertIsInstance(obj[f'Test{index}'],
                                  Parameter)

    def test_add_params__with_kwarg_wrong_type(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(TypeError):
            obj.add_params(Test5=1)

    def test_add_params__mixed(self):
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

    def test_add_params__collection(self):
        obj = ParameterCollection(*self._params)
        coll = ParameterCollection(Parameter('Test7', str, default='Test'),
                                    Parameter('Test8', float, default=0))
        obj.add_params(coll)
        for index in range(7, 9):
            self.assertIsInstance(obj[f'Test{index}'],
                                  Parameter)

    def test_add_params__duplicate(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.add_params(Parameter('Test5', float, default=-1),
                            Test5=Parameter('Test5', int, default=12))
        with self.assertRaises(KeyError):
            obj.add_params(Parameter('Test5', float, default=-1),
                            Parameter('Test5', int, default=12))

    def test_check_arg_types__with_params(self):
        obj = ParameterCollection()
        obj._ParameterCollection__check_arg_types(*self._params)
        # assert does not raise Exception

    def test_check_arg_types__with_collection(self):
        tester = ParameterCollection(*self._params)
        obj = ParameterCollection()
        obj._ParameterCollection__check_arg_types(tester)
        # assert does not raise Exception

    def test_check_arg_types__wrong_type(self):
        obj = ParameterCollection()
        with self.assertRaises(TypeError):
            obj._ParameterCollection__check_arg_types([0])

    def test_add_param___with_parameter(self):
        obj = ParameterCollection()
        obj.add_param(self._params[0])

    def test_add_param___with_collection(self):
        tester = ParameterCollection(*self._params)
        obj = ParameterCollection()
        with self.assertRaises(TypeError):
            obj.add_param(tester)

    def test_add_param___with_list(self):
        obj = ParameterCollection()
        with self.assertRaises(TypeError):
            obj.add_param(self._params)

    def test_check_key_available__empty(self):
        obj = ParameterCollection()
        obj._ParameterCollection__check_key_available(self._params[0])
        # assert does not raise Exception

    def test_check_key_available__with_intrinsic_keys(self):
        obj = ParameterCollection(*self._params[1:])
        obj._ParameterCollection__check_key_available(self._params[0])
        # assert does not raise Exception

    def test_check_key_available__with_external_empty_keys(self):
        obj = ParameterCollection(*self._params)
        obj._ParameterCollection__check_key_available(self._params[0], keys={})
        # assert does not raise Exception

    def test_check_key_available__key_taken(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj._ParameterCollection__check_key_available(self._params[0])

    def test_check_key_available__with_external_key_taken(self):
        tester = ParameterCollection(*self._params)
        obj = ParameterCollection()
        with self.assertRaises(KeyError):
            obj._ParameterCollection__check_key_available(
                self._params[0], keys=tester.keys())

    def test_raise_type_error(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(TypeError):
            obj._ParameterCollection__raise_type_error('test')

    def test_set_item__correct(self):
        obj = ParameterCollection(*self._params)
        obj['Test5'] = Parameter('Test5', float, default=-1)
        self.assertTrue('Test5' in obj.keys())

    def test_set_item__wrong_type(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(TypeError):
            obj['Test6'] = 12

    def test_set_item__duplicate_key(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj['Test6'] = Parameter('Test5', float, default=-1)

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

    def test_values_equal__wrong_key(self):
        obj = ParameterCollection(*self._params)
        with self.assertRaises(KeyError):
            obj.values_equal('Test2', 'Test6')

    def test_values_equal__different_values(self):
        obj = ParameterCollection(*self._params)
        self.assertFalse(obj.values_equal('Test2', 'Test3'))

    def test_values_equal__same_values(self):
        obj = ParameterCollection(*self._params)
        self.assertTrue(obj.values_equal('Test0', 'Test3'))



if __name__ == "__main__":
    unittest.main()
