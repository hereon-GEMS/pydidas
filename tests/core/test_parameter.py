# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import pickle
import unittest
import warnings
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from pydidas.core import Hdf5key, UserConfigError
from pydidas.core.parameter import Parameter, _get_base_class
from pydidas.core.utils import get_random_string


TYPES_AND_VALS = [
    [int, 12],
    [float, 3.6],
    [str, "spam"],
    [list, [1, 2, 2]],
    [tuple, (0, 2, 42)],
]


class TestParameter(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore")

    def tearDown(self): ...

    def test_get_base_class(self):
        test_cases = [
            (None, None),
            (int, Integral),
            (np.int32, Integral),
            (np.int16, Integral),
            (np.uint32, Integral),
            (np.uint8, Integral),
            (float, Real),
            (np.float32, Real),
            (np.float64, Real),
        ]
        for dtype, expected in test_cases:
            with self.subTest(dtype=dtype):
                self.assertEqual(_get_base_class(dtype), expected)

    def test_creation(self):
        obj = Parameter("Test0", int, 12)
        self.assertIsInstance(obj, Parameter)

    def test_creation__no_arguments(self):
        with self.assertRaises(TypeError):
            Parameter()

    def test_creation__with_meta_dict(self):
        obj = Parameter("Test0", int, 0, dict())
        self.assertIsInstance(obj, Parameter)

    def test_creation__missing_default(self):
        with self.assertRaises(TypeError):
            Parameter("Test0", int)

    def test_creation__wrong_choices(self):
        with self.assertRaises(ValueError):
            Parameter("Test0", int, 12, choices=[0, 10])

    def test_creation__choices_wrong_type(self):
        with self.assertRaises(TypeError):
            Parameter("Test0", int, 12, choices=12)

    def test_creation__wrong_datatype(self):
        with self.assertRaises(TypeError):
            Parameter("Test0", int, "12b")

    def test_creation__w_choices_and_range(self):
        with self.assertRaises(UserConfigError):
            Parameter("Test0", int, 12, choices=[0, 6, 12], range=(0, 12))

    def test_creation__with_allow_None(self):
        param = Parameter("Test0", int, 12, allow_None=True)
        self.assertTrue(param._Parameter__meta["allow_None"])

    def test_typecheck__no_type(self):
        param = Parameter("Test0", None, 12)
        for item in [12, "12", None, [1, 2, 3]]:
            self.assertTrue(param._Parameter__typecheck(item))

    def test_typecheck__int(self):
        param = Parameter("Test0", int, 12)
        self.assertTrue(param._Parameter__typecheck(12))
        for item in ["12", None, [1, 2, 3]]:
            self.assertFalse(param._Parameter__typecheck(item))

    def test_typecheck__list_of_int(self):
        param = Parameter("Test0", list, [1, 2, 3], subtype=int)
        _cases = [[True, [1, 3]], [False, [1, "3"]], [False, [1, 3.0]]]
        for _exp, _val in _cases:
            with self.subTest(input=_val):
                self.assertEqual(param._Parameter__typecheck(_val), _exp)

    def test_typecheck__int_w_allow_none(self):
        param = Parameter("Test0", int, 12, allow_None=True)
        self.assertTrue(param._Parameter__typecheck(12))
        self.assertTrue(param._Parameter__typecheck(None))

    def test_call(self):
        obj = Parameter("Test0", int, 12)
        self.assertEqual(obj(), 12)

    def test_name(self):
        obj = Parameter("Test0", int, 12, name="Test0")
        self.assertEqual(obj.name, "Test0")

    def test_refkey(self):
        obj = Parameter("Test0", int, 12)
        self.assertEqual(obj.refkey, "Test0")

    def test_default(self):
        obj = Parameter("Test0", int, 12)
        self.assertEqual(obj.default, 12)

    def test_default_with_different_value(self):
        obj = Parameter("Test0", int, 12)
        obj.value = 0
        self.assertEqual(obj.default, 12)

    def test_unit(self):
        obj = Parameter("Test0", int, 12, unit="The_unit")
        self.assertEqual(obj.unit, "The_unit")

    def test_unit__wrong_type(self):
        obj = Parameter("Test0", int, 12, unit=42)
        self.assertEqual(obj.unit, "42")

    def test_unit__w_None(self):
        obj = Parameter("Test0", int, 12, unit=None)
        self.assertEqual(obj.unit, "")
        self.assertIsInstance(obj.unit, str)

    def test_tooltip__int(self):
        obj = Parameter("Test0", int, 12, unit="m", value=10, tooltip="Test tooltip")
        self.assertEqual(obj.tooltip, "Test tooltip (unit: m, type: integer)")

    def test_tooltip__float(self):
        obj = Parameter("Test0", float, 12, unit="m", value=10, tooltip="Test tooltip")
        self.assertEqual(obj.tooltip, "Test tooltip (unit: m, type: float)")

    def test_tooltip__str(self):
        obj = Parameter("Test0", str, "", unit="m", tooltip="Test tooltip")
        self.assertEqual(obj.tooltip, "Test tooltip (unit: m, type: str)")

    def test_tooltip__Hdf5key(self):
        obj = Parameter("Test0", Hdf5key, "", unit="m", tooltip="Test tooltip")
        self.assertEqual(obj.tooltip, "Test tooltip (unit: m, type: Hdf5key)")

    def test_tooltip__path(self):
        obj = Parameter("Test0", Path, "", unit="m", tooltip="Test tooltip")
        self.assertEqual(obj.tooltip, "Test tooltip (unit: m, type: Path)")

    def test_tooltip__other(self):
        obj = Parameter(
            "Test0", np.ndarray, np.zeros(3), unit="m", tooltip="Test tooltip"
        )
        self.assertEqual(
            obj.tooltip, "Test tooltip (unit: m, type: <class 'numpy.ndarray'>)"
        )

    def test_choices_setter(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        self.assertEqual(obj.choices, [0, 12])

    def test_choices_setter__update_to_None(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        obj.choices = [0, 12, 24]
        obj.choices = None
        obj.value = 127
        self.assertIsNone(obj.choices)

    def test_choices_setter__update(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        obj.choices = [0, 12, 24]
        self.assertEqual(obj.choices, [0, 12, 24])

    def test_choices_setter__wrong_type(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        with self.assertRaises(TypeError):
            obj.choices = dict(a=0, b=12)

    def test_choices_setter__value_not_included(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        with self.assertRaises(ValueError):
            obj.choices = [0, 24]

    def test_choices_setter__wrong_entry(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        with self.assertRaises(ValueError):
            obj.choices = [12, "24"]

    def test_optional(self):
        obj = Parameter("Test0", int, 12)
        self.assertEqual(obj.optional, False)

    def test_optional_true(self):
        obj = Parameter("Test0", int, 12, optional=True)
        self.assertEqual(obj.optional, True)

    def test_dtype__int(self):
        obj = Parameter("Test0", int, 12)
        self.assertEqual(obj.dtype, Integral)

    def test_dtype_float(self):
        obj = Parameter("Test0", float, 12)
        self.assertEqual(obj.dtype, Real)

    def test_get_value(self):
        obj = Parameter("Test0", int, 12)
        self.assertEqual(obj.value, 12)

    def test_get_allow_None(self):
        obj = Parameter("Test0", int, 12, allow_None=True)
        self.assertTrue(obj.allow_None)

    def test_set_value(self):
        obj = Parameter("Test0", int, 12)
        obj.value = 24
        self.assertEqual(obj.value, 24)

    def test_set_value__w_allow_None(self):
        obj = Parameter("Test0", int, 12, allow_None=True)
        obj.value = None
        self.assertEqual(obj.value, None)

    def test_set_value__wrong_type(self):
        obj = Parameter("Test0", int, 12)
        with self.assertRaises(ValueError):
            obj.value = "24b"

    def test_set_value_wrong_choice(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        with self.assertRaises(ValueError):
            obj.value = 24

    def test_set_value__float(self):
        _val = 24.0
        obj = Parameter("Test0", float, 12)
        obj.value = np.float64(_val)
        self.assertEqual(obj.value, _val)
        self.assertEqual(type(obj.value), float)

    def test_set_value__w_valid_range(self):
        _val = 24.0
        for _type in [int, float, np.float64, np.uint8]:
            with self.subTest(datatype=_type):
                obj = Parameter("Test0", _type, 12, range=(0, 42))
                obj.value = np.float64(_val)
                self.assertEqual(obj.value, _val)
                self.assertEqual(
                    type(obj.value), int if _type in [int, np.uint8] else float
                )

    def test_set_value__float_w_invalid_range(self):
        _val = 24.0
        for _type in [int, float, np.float64, np.uint8]:
            with self.subTest(datatype=_type):
                obj = Parameter("Test0", _type, 12, range=(0, 12))
                with self.assertRaises(UserConfigError):
                    obj.value = _val

    def test_set_value__w_range_to_None(self):
        _val = 24.0
        obj = Parameter("Test0", float, 12, range=(0, 12), allow_None=True)
        obj.value = None
        self.assertIsNone(obj.value)

    def test_set_value__tuple_w_subtype(self):
        _vals = ((1, 2, 3), (12, 24.0), (12, "42"))
        for _val in _vals:
            _ref = tuple([int(_v) for _v in _val])
            with self.subTest(input=_val):
                obj = Parameter("Test0", tuple, (1, 2), subtype=int)
                obj.value = _val
                self.assertEqual(obj.value, _ref)

    def test_set_value__tuple_w_subtype_wrong_type(self):
        _val = (1, 2, "3b")
        obj = Parameter("Test0", tuple, (1, 2), subtype=int)
        with self.assertRaises(ValueError):
            obj.value = _val

    def test_get_range(self):
        obj = Parameter("Test0", int, 12)
        for _key in ["123", (1, 54, 4), [1, 2, 3], {1: "a", "b": 42}]:
            with self.subTest(range=_key):
                obj._Parameter__meta["range"] = _key
                self.assertEqual(obj.range, _key)

    def test_set_range(self):
        for _type in [int, float, np.float64, np.uint8]:
            for _range in [[0, 12], (3, 42), np.array((3, 2))]:
                with self.subTest(datatype=_type, range=_range):
                    obj = Parameter("Test0", _type, 12)
                    obj.range = _range
                    self.assertEqual(obj.range, tuple(_range))

    def test_set_range__no_number_type(self):
        obj = Parameter("Test0", str, "12")
        with self.assertRaises(UserConfigError):
            obj.range = (4, 42)

    def test_set_range__with_choices(self):
        obj = Parameter("Test0", int, 12, choices=[0, 12])
        with self.assertRaises(UserConfigError):
            obj.range = (4, 42)

    def test_set_range__set_to_None(self):
        obj = Parameter("Test0", int, 12, range=(4, 42))
        obj.range = None
        self.assertIsNone(obj.range)

    def test_set_range__wrong_length(self):
        obj = Parameter("Test0", int, 12)
        with self.assertRaises(UserConfigError):
            obj.range = (4, 42, 12)

    def test_set_range__wrong_dtype(self):
        obj = Parameter("Test0", int, 12)
        with self.assertRaises(ValueError):
            obj.range = (4, "b")

    def test_restore_default(self):
        obj = Parameter("Test0", int, 12)
        obj.value = 24
        obj.restore_default()
        self.assertEqual(obj.value, 12)

    def test_copy(self):
        obj = Parameter("Test0", int, 12)
        _copy = obj.copy()
        self.assertNotEqual(obj, _copy)
        self.assertIsInstance(_copy, Parameter)

    def test_get_value_for_export__with_Path(self):
        obj = Parameter("Test0", Path, Path())
        _val = obj.value_for_export
        self.assertIsInstance(_val, str)

    def test_get_value_for_export__with_Hdf5key(self):
        obj = Parameter("Test0", Hdf5key, Hdf5key("/test"))
        _val = obj.value_for_export
        self.assertIsInstance(_val, str)

    def test_get_value_for_export__with_str(self):
        obj = Parameter("Test0", str, "/test")
        _val = obj.value_for_export
        self.assertIsInstance(_val, str)

    def test_get_value_for_export__with_float(self):
        obj = Parameter("Test0", float, 12.34)
        _val = obj.value_for_export
        self.assertIsInstance(_val, Real)

    def test_get_value_for_export__with_int(self):
        obj = Parameter("Test0", int, 27)
        _val = obj.value_for_export
        self.assertIsInstance(_val, Integral)

    def test_get_value_for_export__with_list(self):
        obj = Parameter("Test0", list, [27])
        _val = obj.value_for_export
        self.assertIsInstance(_val, list)

    def test_get_value_for_export__with_tuple(self):
        obj = Parameter("Test0", tuple, (27,))
        _val = obj.value_for_export
        self.assertIsInstance(_val, tuple)

    def test_get_value_for_export__with_dict(self):
        obj = Parameter("Test0", dict, {1: "a", "b": 42})
        _val = obj.value_for_export
        self.assertIsInstance(_val, dict)

    def test_get_value_for_export__with_NoneType(self):
        obj = Parameter("Test0", None, 27.7)
        with self.assertRaises(TypeError):
            obj.value_for_export

    def test_set_value_and_choices__wrong_type(self):
        obj = Parameter("Test0", float, 27.7)
        with self.assertRaises(ValueError):
            obj.set_value_and_choices("test", [12, 14])

    def test_set_value_and_choices__None_type_allowed(self):
        obj = Parameter("Test0", float, 27.7, allow_None=True)
        with self.assertRaises(ValueError):
            obj.set_value_and_choices(None, [12, 14])

    def test_set_value_and_choices__value_not_in_choices(self):
        obj = Parameter("Test0", float, 27.7)
        with self.assertRaises(ValueError):
            obj.set_value_and_choices(3, [12, 14])

    def test_set_value_and_choices__w_range_set(self):
        obj = Parameter("Test0", float, 27.7, range=(0, 42))
        with self.assertRaises(UserConfigError):
            obj.set_value_and_choices(12, [12, 14])

    def test_set_value_and_choices__w_no_new_choices(self):
        obj = Parameter("Test0", int, 2, choices=[1, 2, 3])
        obj.set_value_and_choices(12, None)
        self.assertIsNone(obj.choices)
        self.assertEqual(obj.value, 12)

    def test_set_value_and_choices__valid(self):
        _val = 3.12
        _choices = [3.12, 34.2, 42.1]
        obj = Parameter("Test0", float, 27.7)
        obj.set_value_and_choices(_val, _choices)
        self.assertEqual(obj.value, _val)
        self.assertEqual(obj.choices, _choices)

    def test_dump(self):
        for _type, _val in TYPES_AND_VALS:
            _ret_type = (
                Integral if _type is int else (Real if _type is float else _type)
            )
            with self.subTest(datatype=_type, value=_val):
                obj = Parameter("Test0", _type, _val)
                dump = obj.dump()
                self.assertEqual(dump[0], "Test0")
                self.assertEqual(dump[1], _ret_type)
                self.assertEqual(dump[2], _val)
                self.assertEqual(
                    dump[3],
                    {
                        "tooltip": "",
                        "unit": "",
                        "optional": False,
                        "name": "",
                        "allow_None": False,
                        "choices": None,
                        "subtype": None,
                        "range": None,
                        "value": _val,
                    },
                )

    def test_load_from_dump(self):
        for _type, _val in TYPES_AND_VALS:
            with self.subTest(datatype=_type, value=_val):
                obj = Parameter("Test0", _type, _val)
                obj2 = Parameter(*obj.dump())
                for _key in obj.__dict__:
                    self.assertEqual(obj.__dict__[_key], obj2.__dict__[_key])

    def test_copy__(self):
        obj = Parameter("Test0", int, 12)
        _copy = copy.copy(obj)
        self.assertNotEqual(obj, _copy)
        self.assertIsInstance(_copy, Parameter)

    def test_copy__with_choices(self):
        obj = Parameter("Test0", int, 12, choices=[12, 15, 18])
        obj.set_value_and_choices(16, [16, 19, 22])
        _copy = copy.copy(obj)
        self.assertNotEqual(obj, _copy)
        self.assertIsInstance(_copy, Parameter)

    def test_repr__(self):
        obj = Parameter("Test0", int, 12, optional=True)
        _r = obj.__repr__()
        self.assertIsInstance(_r, str)

    def test_convenience_type_conversion__None(self):
        _cases = [None, "None", ""]
        obj = Parameter("Test0", int, 12, allow_None=True)
        for _case in _cases:
            with self.subTest(input=_case):
                _new_val = obj._Parameter__convenience_type_conversion(_case)
                self.assertEqual(_new_val, None)

    def test_convenience_type_conversion_any(self):
        _val = 42
        obj = Parameter("Test0", int, 12)
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertEqual(_val, _new_val)

    def test_convenience_type_conversion__str_to_bool(self):
        for _val in ["True", "False"]:
            with self.subTest(input=_val):
                obj = Parameter("Test0", int, 1, choices=[True, False])
                _new_val = obj._Parameter__convenience_type_conversion(_val)
                self.assertEqual(_new_val, _val == "True")

    def test_convenience_type_conversion__float_w_string_number_input(self):
        _val = "42"
        obj = Parameter("Test0", float, 12.2)
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertEqual(float(_val), _new_val)

    def test_convenience_type_conversion__float_w_string_input(self):
        _val = "42a"
        obj = Parameter("Test0", float, 12.2)
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertEqual(_val, _new_val)

    def test_convenience_type_conversion__int_w_string_number_input(self):
        _val = "42"
        obj = Parameter("Test0", int, 12)
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertEqual(int(_val), _new_val)

    def test_convenience_type_conversion__int_w_string_input(self):
        _val = "42a"
        obj = Parameter("Test0", int, 12)
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertEqual(_val, _new_val)

    def test_convenience_type_conversion_path(self):
        _val = __file__
        obj = Parameter("Test0", Path, "")
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertIsInstance(_new_val, Path)

    def test_convenience_type_conversion_list(self):
        _val = [1, 2, 3]
        obj = Parameter("Test0", tuple, (1, 2))
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertIsInstance(_new_val, tuple)
        self.assertEqual(_new_val, tuple(_val))

    def test_convenience_type_conversion__list_w_string__no_subtype(self):
        _val = "[1, 2, 3]"
        obj = Parameter("Test0", tuple, (1, 2))
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertIsInstance(_new_val, str)
        self.assertEqual(_new_val, "[1, 2, 3]")

    def test_convenience_type_conversion__iterable_w_string__w_subtype(self):
        for _val in ["[1, 2, 3, 5]", "(1, 2, 3, 5)", "{1, 2, 3, 5}"]:
            with self.subTest(input=_val):
                obj = Parameter("Test0", tuple, (1, 2), subtype=int)
                _new_val = obj._Parameter__convenience_type_conversion(_val)
                self.assertIsInstance(_new_val, tuple)
                self.assertEqual(_new_val, (1, 2, 3, 5))

    def test_convenience_type_conversion_tuple(self):
        _val = (1, 2, 3)
        obj = Parameter("Test0", list, [1])
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertIsInstance(_new_val, list)

    def test_convenience_type_conversion_Hdf5key(self):
        _val = "/new/test"
        obj = Parameter("Test0", Hdf5key, "/test")
        _new_val = obj._Parameter__convenience_type_conversion(_val)
        self.assertIsInstance(_new_val, Hdf5key)

    def test_hash__simple_str(self):
        _param = Parameter("Test", str, "")
        _param2 = Parameter("Test", str, "")
        self.assertEqual(hash(_param), hash(_param2))

    def test_hash__full_str(self):
        _param = Parameter("Test", str, get_random_string(12), name="Name")
        _param2 = Parameter("Test", str, _param.value, name="Name")
        self.assertEqual(hash(_param), hash(_param2))

    def test_hash__different_str(self):
        _param = Parameter("Test", str, get_random_string(12), name="Name")
        _param2 = Parameter("Test", str, get_random_string(12), name="Name")
        self.assertNotEqual(hash(_param), hash(_param2))

    def test_hash__simple_int(self):
        _param = Parameter("Test", int, 0)
        _param2 = Parameter("Test", int, 0)
        self.assertEqual(hash(_param), hash(_param2))

    def test_hash__full_int(self):
        _param = Parameter("Test", int, 0, name="The name", unit="m")
        _param2 = Parameter("Test", int, 0, name="The name", unit="m")
        _param.value = 42
        _param2.value = 42
        self.assertEqual(hash(_param), hash(_param2))

    def test_hash__different_int_value(self):
        _param = Parameter("Test", int, 0, name="The name", unit="m")
        _param2 = Parameter("Test", int, 0, name="The name", unit="m")
        _param.value = 42
        _param2.value = 41
        self.assertNotEqual(hash(_param), hash(_param2))

    def test_hash__non_hashable_type(self):
        _param = Parameter("Test", None, [0, 1], name="The name", unit="m")
        self.assertIsInstance(hash(_param), int)

    def test_hash__compare_non_hashable_type(self):
        _param = Parameter("Test", None, [0, 1], name="The name", unit="m")
        _param2 = Parameter("Test", None, [0, 2], name="The name", unit="m")
        _param3 = Parameter("Test", None, [0, 1], name="Other name", unit="m")
        self.assertEqual(hash(_param), hash(_param2))
        self.assertNotEqual(hash(_param), hash(_param3))

    def test_with_ndarray__value_property(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        self.assertIsInstance(_param.value, np.ndarray)

    def test_with_ndarray__copy(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _param2 = _param.copy()
        self.assertIsInstance(_param2.value, np.ndarray)
        self.assertNotEqual(id(_param.value), id(_param2.value))

    def test_with_ndarray__hash(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _param2 = Parameter("Test", np.ndarray, np.zeros(3))
        self.assertEqual(hash(_param), hash(_param2))

    def test_with_ndarray__repr(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _param.value = np.asarray([1, 42, 5, 7])
        _repr = _param.__repr__()
        self.assertIsInstance(_repr, str)

    def test_with_ndarray__str(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _param.value = np.asarray([1, 42, 5, 7])
        _repr = _param.__str__()
        self.assertIsInstance(_repr, str)

    def test_with_ndarray__pickle(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _dump = pickle.dumps(_param)
        _param2 = pickle.loads(_dump)
        self.assertTrue(np.allclose(_param.value, _param2.value))
        self.assertEqual(_param.refkey, _param2.refkey)

    def test_with_ndarray__value_as_list(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _list = [1, 42, 5, 7]
        _param.value = _list
        self.assertTrue(np.allclose(_param.value, np.array(_list)))

    def test_with_ndarray__value_for_export(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _exported_val = _param.value_for_export
        self.assertIsInstance(_exported_val, list)
        self.assertEqual(_exported_val, list(_param.value))

    def test_with_ndarray__deepcopy(self):
        _param = Parameter("Test", np.ndarray, np.zeros(3))
        _h = hash(_param)
        self.assertIsInstance(_h, int)


if __name__ == "__main__":
    unittest.main()
