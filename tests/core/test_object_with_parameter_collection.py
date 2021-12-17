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
import io
import sys
import copy
import pickle

from pydidas.core import (ObjectWithParameterCollection, Parameter,
                          ParameterCollection)


class TestObjectWithParameterCollection(unittest.TestCase):

    def setUp(self):
        self._params = ParameterCollection(
            Parameter('Test0', int, default=12),
            Parameter('Test1', str, default='test str'),
            Parameter('Test2', int, default=3),
            Parameter('Test3', float, default=12))

    def tearDown(self):
        ...

    def test_creation(self):
        obj = ObjectWithParameterCollection()
        self.assertIsInstance(obj, ObjectWithParameterCollection)

    def test_add_params__with_args(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(*self._params.values())
        for index in range(4):
            self.assertEqual(obj.params[f'Test{index}'],
                             self._params.get(f'Test{index}'))

    def test_add_params__with_dict(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        for index in range(4):
            self.assertEqual(obj.params[f'Test{index}'],
                             self._params.get(f'Test{index}'))

    def test_add_params__wrong_type(self):
        obj = ObjectWithParameterCollection()
        with self.assertRaises(TypeError):
            obj.add_params(['test'])

    def test_add_params__with_kwargs(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(param1=self._params.get('Test0'),
                       param2=self._params.get('Test1'),
                       param3=self._params.get('Test2'),
                       param4=self._params.get('Test3'),
                       )
        for index in range(4):
            self.assertEqual(obj.params[f'Test{index}'],
                             self._params.get(f'Test{index}'))

    def test_add_param(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.add_param(Parameter('Test5', float, default=-1))
        self.assertIsInstance(obj.get_param('Test5'), Parameter)

    def test_add_param__duplicate(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.add_param(Parameter('Test5', float, default=-1))
        with self.assertRaises(KeyError):
            obj.add_param(Parameter('Test5', float, default=-1))

    def test_get_param__wrong_key(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(KeyError):
            obj.get_param('no such param')

    def test_get_param(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _p = obj.get_param('Test0')
        self.assertIsInstance(_p, Parameter)
        self.assertEqual(_p, obj.params['Test0'])

    def test_get_params__empty(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _res = obj.get_params()
        self.assertEqual(_res, [])

    def test_get_params__single(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _res = obj.get_params('Test0')
        self.assertEqual(_res, [self._params['Test0']])

    def test_get_params__multiple(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _res = obj.get_params('Test0', 'Test2')
        self.assertEqual(_res, [self._params['Test0'], self._params['Test2']])

    def test_get_param_value(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        self.assertEqual(obj.get_param_value('Test2'), 3)

    def test_get_param_value__no_key(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(KeyError):
            obj.get_param_value('Test5')

    def test_get_param_value__no_key_with_default(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _default = 124.434
        self.assertEqual(obj.get_param_value('Test5', _default), _default)

    def test_print_param_values(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        obj.print_param_values()
        self.assertTrue(len(mystdout.getvalue()) > 0)
        sys.stdout = old_stdout

    def test_set_param_value(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.set_param_value('Test2', 12)
        self.assertEqual(obj.get_param_value('Test2'), 12)

    def test_get_param_keys(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        self.assertEqual(obj.get_param_keys(), list(obj.params.keys()))

    def test_set_param_value__no_key(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(KeyError):
            obj.set_param_value('Test5', 12)

    def test_check_key(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(KeyError):
            obj._check_key('NoKey')

    def test_check_key__correct_key(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj._check_key('Test0')

    def test_get_param_value_with_modulo(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _mod = 10
        _test = obj.get_param_value('Test0')
        _new = obj._get_param_value_with_modulo('Test0', _mod)
        self.assertEqual(_new, _test % _mod)

    def test_get_param_value_with_modulo__equal(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _test = obj.get_param_value('Test0')
        _new = obj._get_param_value_with_modulo('Test0', _test)
        self.assertEqual(_new, _test)

    def test_get_param_value_with_modulo__negative(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.set_param_value('Test0', -1)
        _mod = 10
        _new = obj._get_param_value_with_modulo('Test0', _mod)
        self.assertEqual(_new, _mod)

    def test_get_param_value_with_modulo__none_type_low(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(Parameter('Test0', int, 12, allow_None=True))
        obj.set_param_value('Test0', None)
        _mod = 10
        _new = obj._get_param_value_with_modulo('Test0', _mod, none_low=True)
        self.assertEqual(_new, 0)

    def test_get_param_value_with_modulo__none_type_high(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(Parameter('Test0', int, 12, allow_None=True))
        obj.set_param_value('Test0', None)
        _mod = 10
        _new = obj._get_param_value_with_modulo('Test0', _mod, none_low=False)
        self.assertEqual(_new, _mod)

    def test_get_param_value_with_modulo__not_integer(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(ValueError):
            obj._get_param_value_with_modulo('Test3', 10)

    def test_get_default_params_copy(self):
        defaults = ObjectWithParameterCollection.get_default_params_copy()
        self.assertIsInstance(defaults, ParameterCollection)

    def test_set_default_params(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.default_params = ParameterCollection(
            Parameter('Test0', int, default=10),
            Parameter('Test5', str, default='test str'),
            Parameter('Test6', float, default=-1))
        obj.set_default_params()
        self.assertEqual(obj.get_param_value('Test0'), 12)
        self.assertEqual(obj.get_param_value('Test5'), 'test str')
        self.assertEqual(obj.get_param_value('Test6'), -1)

    def test_restore_all_defaults__no_confirm(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.set_param_value('Test2', 12)
        obj.restore_all_defaults()
        self.assertEqual(obj.get_param_value('Test2'), 12)

    def test_restore_all_defaults(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.set_param_value('Test2', 12)
        obj.restore_all_defaults(True)
        self.assertEqual(obj.get_param_value('Test2'),
                         self._params['Test2'].default)

    def test_copy(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj2 = copy.copy(obj)
        self.assertIsInstance(obj2, ObjectWithParameterCollection)

    def test_getstate(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj._config['test'] = 'Test'
        _state = obj.__getstate__()
        for _key, _param in _state['params'].items():
            self.assertEqual(_param.value, obj.get_param_value(_key))
        for _key, _value in _state['_config'].items():
            self.assertEqual(_value, obj._config[_key])

    def test_setstate(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        _state = {'params': obj.params.get_copy(),
                  '_config': {'test_key': True, 'another_key': 'entry'}}
        obj.__setstate__(_state)
        for _key, _param in _state['params'].items():
            self.assertEqual(_param.value, obj.get_param_value(_key))
        for _key, _value in _state['_config'].items():
            self.assertEqual(_value, obj._config[_key])

    def test_pickle(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        new_obj = pickle.loads(pickle.dumps(obj))
        self.assertIsInstance(new_obj, ObjectWithParameterCollection)
        for _key, _param in obj.params.items():
            self.assertEqual(_param.value, new_obj.get_param_value(_key))

if __name__ == "__main__":
    unittest.main()
