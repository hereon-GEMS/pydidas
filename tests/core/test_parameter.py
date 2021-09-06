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
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from pydidas.core import Parameter, HdfKey
from pydidas.core.parameter import _get_base_class


class TestParameter(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_base_class__None(self):
        _cls = _get_base_class(None)
        self.assertEqual(_cls, None)

    def test_get_base_class__generic_int(self):
        _cls = _get_base_class(int)
        self.assertEqual(_cls, Integral)

    def test_get_base_class__np_int32(self):
        _cls = _get_base_class(np.int32)
        self.assertEqual(_cls, Integral)

    def test_get_base_class__np_int16(self):
        _cls = _get_base_class(np.int16)
        self.assertEqual(_cls, Integral)

    def test_get_base_class__np_uint32(self):
        _cls = _get_base_class(np.uint32)
        self.assertEqual(_cls, Integral)

    def test_get_base_class__np_uint8(self):
        _cls = _get_base_class(np.uint8)
        self.assertEqual(_cls, Integral)

    def test_get_base_class__generic_float(self):
        _cls = _get_base_class(float)
        self.assertEqual(_cls, Real)

    def test_get_base_class__np_float32(self):
        _cls = _get_base_class(np.float32)
        self.assertEqual(_cls, Real)

    def test_get_base_class__np_float64(self):
        _cls = _get_base_class(np.float64)
        self.assertEqual(_cls, Real)

    def test_creation(self):
        obj = Parameter('Test0', int, default=12)
        self.assertIsInstance(obj, Parameter)

    def test_creation_no_arguments(self):
        with self.assertRaises(TypeError):
            Parameter()

    def test_creation_with_meta_dict(self):
        obj = Parameter('Test0', int, dict(default=12))
        self.assertIsInstance(obj, Parameter)

    def test_creation_missing_default(self):
        with self.assertRaises(TypeError):
            Parameter('Test0', int)

    def test_creation_wrong_choices(self):
        with self.assertRaises(ValueError):
            Parameter('Test0', int, default=12, choices=[0, 10])

    def test_creation_choices_wrong_type(self):
        with self.assertRaises(TypeError):
            Parameter('Test0', int, default=12, choices=12)

    def test_creation_wrong_datatype(self):
        with self.assertRaises(TypeError):
            Parameter('Test0', int, default='12')

    def test_call(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj(), 12)

    def test_name(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.name, 'Test0')

    def test_refkey(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.refkey, 'Test0')

    def test_refkey_ii(self):
        obj = Parameter('Test0', int, default=12, refkey='key')
        self.assertEqual(obj.refkey, 'key')

    def test_default(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.default, 12)

    def test_default_with_different_value(self):
        obj = Parameter('Test0', int, default=12)
        obj.value = 0
        self.assertEqual(obj.default, 12)

    def test_unit(self):
        obj = Parameter('Test0', int, default=12, unit='The_unit')
        self.assertEqual(obj.unit, 'The_unit')

    def test_tooltip_int(self):
        obj = Parameter('Test0', int, default=12, unit='m', value=10,
                        tooltip='Test tooltip')
        self.assertEqual(obj.tooltip, 'Test tooltip (unit: m, type: integer)')

    def test_tooltip_float(self):
        obj = Parameter('Test0', float, default=12, unit='m', value=10,
                        tooltip='Test tooltip')
        self.assertEqual(obj.tooltip, 'Test tooltip (unit: m, type: float)')

    def test_tooltip_str(self):
        obj = Parameter('Test0', str, default='', unit='m',
                        tooltip='Test tooltip')
        self.assertEqual(obj.tooltip, 'Test tooltip (unit: m, type: str)')

    def test_tooltip_hdfkey(self):
        obj = Parameter('Test0', HdfKey, default='', unit='m',
                        tooltip='Test tooltip')
        self.assertEqual(obj.tooltip, 'Test tooltip (unit: m, type: HdfKey)')

    def test_tooltip_path(self):
        obj = Parameter('Test0', Path, default='', unit='m',
                        tooltip='Test tooltip')
        self.assertEqual(obj.tooltip, 'Test tooltip (unit: m, type: Path)')

    def test_tooltip_other(self):
        obj = Parameter('Test0', np.ndarray, default=np.zeros((3)), unit='m',
                        tooltip='Test tooltip')
        self.assertEqual(
            obj.tooltip,
            "Test tooltip (unit: m, type: <class 'numpy.ndarray'>)")

    def test_choices_setter(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        self.assertEqual(obj.choices, [0, 12])

    def test_choices_setter_update(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        obj.choices = [0, 12, 24]
        self.assertEqual(obj.choices, [0, 12, 24])

    def test_choices_setter_wrong_type(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        with self.assertRaises(TypeError):
            obj.choices = dict(a=0, b=12)

    def test_choices_setter_value_not_included(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        with self.assertRaises(ValueError):
            obj.choices = [0, 24]

    def test_choices_setter_wrong_entry(self):
        obj = Parameter('Test0', int, default=12, choices=[0,12])
        with self.assertRaises(ValueError):
            obj.choices = [12, '24']

    def test_optional(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.optional, False)

    def test_optional_ii(self):
        obj = Parameter('Test0', int, default=12, optional=True)
        self.assertEqual(obj.optional, True)

    def test_type(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.type, Integral)

    def test_type_ii(self):
        obj = Parameter('Test0', float, default=12)
        self.assertEqual(obj.type, Real)

    def test_get_value(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.value, 12)

    def test_set_value(self):
        obj = Parameter('Test0', int, default=12)
        obj.value = 24
        self.assertEqual(obj.value, 24)

    def test_set_value_wrong_type(self):
        obj = Parameter('Test0', int, default=12)
        with self.assertRaises(ValueError):
            obj.value = '24'

    def test_set_value_wrong_choice(self):
        obj = Parameter('Test0', int, default=12, choices=[0, 12])
        with self.assertRaises(ValueError):
            obj.value = 24

    def test_restore_default(self):
        obj = Parameter('Test0', int, default=12)
        obj.value = 24
        obj.restore_default()
        self.assertEqual(obj.value, 12)

    def test_get_copy(self):
        obj = Parameter('Test0', int, default=12)
        copy = obj.get_copy()
        self.assertNotEqual(obj, copy)
        self.assertIsInstance(copy, Parameter)

    def test_dump(self):
        obj = Parameter('Test0', int, default=12)
        self.assertEqual(obj.name, 'Test0')
        dump = obj.dump()
        self.assertEqual(dump[0], 'Test0')
        self.assertEqual(dump[1], Integral)
        self.assertEqual(dump[2],  {'default': 12,
                                    'tooltip': '',
                                    'unit': '',
                                    'optional': False,
                                    'refkey': 'Test0',
                                    'choices': None,
                                    'value': 12})

    def test__copy__(self):
        obj = Parameter('Test0', int, default=12)
        _copy = copy.copy(obj)
        self.assertNotEqual(obj, _copy)
        self.assertIsInstance(_copy, Parameter)

    def test__repr__(self):
        obj = Parameter('Test0', int, default=12, optional=True)
        _r = obj.__repr__()
        self.assertIsInstance(_r, str)

    def test__convenience_type_conversion_any(self):
        _val = 42
        obj = Parameter('Test0', int, default=12)
        _newval = obj._Parameter__convenience_type_conversion(_val)
        self.assertEqual(_val, _newval)

    def test__convenience_type_conversion_path(self):
        _val = __file__
        obj = Parameter('Test0', Path, default='')
        _newval = obj._Parameter__convenience_type_conversion(_val)
        self.assertIsInstance(_newval, Path)

    def test__convenience_type_conversion_hdfkey(self):
        _val = '/new/test'
        obj = Parameter('Test0', HdfKey, default='/test')
        _newval = obj._Parameter__convenience_type_conversion(_val)
        self.assertIsInstance(_newval, HdfKey)


if __name__ == "__main__":
    unittest.main()
