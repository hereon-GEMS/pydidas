# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from pydidas.core import UserConfigError
from pydidas.core.constants import NUMPY_DTYPES
from pydidas.core.utils.numpy_parser import NumpyParser


_LINSPACE_EXAMPLES = [
    ["np.linspace(5, 6)", np.linspace(5, 6)],
    ["numpy.linspace(2, 10)", np.linspace(2, 10)],
    ["linspace(2, 10, 50)", np.linspace(2, 10, 50)],
    ["np.linspace(2, 10, num=10)", np.linspace(2, 10, num=10)],
    ["np.linspace(-2, 37, num=44)", np.linspace(-2, 37, num=44)],
    ["np.linspace(2, 10, num= 12)", np.linspace(2, 10, num=12)],
    [
        "numpy.linspace(2, 10, endpoint=False)",
        np.linspace(2, 10, endpoint=False),
    ],
    [
        "numpy.linspace(2, 10, endpoint = False)",
        np.linspace(2, 10, endpoint=False),
    ],
    ["linspace(3, 6, 12, False)", np.linspace(3, 6, 12, False)],
    ["linspace(3, 6, num=12, dtype=int)", np.linspace(3, 6, num=12, dtype=int)],
    [
        "linspace(3, 6, dtype=float32, endpoint=False, num=12)",
        np.linspace(3, 6, dtype=np.float32, endpoint=False, num=12),
    ],
]


_ARANGE_EXAMPLES = [
    ["np.arange(5)", np.arange(5)],
    ["numpy.arange(2, 10)", np.arange(2, 10)],
    ["numpy.arange(-124, 17, 23)", np.arange(-124, 17, 23)],
    ["arange(2, 10, 2)", np.arange(2, 10, 2)],
    ["np.arange(2, 10, 2.5)", np.arange(2, 10, 2.5)],
    ["numpy.arange(10, 2, -1)", np.arange(10, 2, -1)],
    ["arange(10, 2, -1.5)", np.arange(10, 2, -1.5)],
    ["arange(2, 42, dtype=None)", np.arange(2, 42, dtype=None)],
    ["arange(10, 2, -1.5)", np.arange(10, 2, -1.5)],
    ["arange(2, 42, 1, dtype=uint8)", np.arange(2, 42, 1, dtype=np.uint8)],
    [
        "arange(2, 42, 1, dtype=np.complex128)",
        np.arange(2, 42, 1, dtype=np.complex128),
    ],
]

_SIMPLE_CASES = [
    "1 2 -3 .4 5",
    "1, 2, -3, 0.4, 5",
    "1,2,-3,.4,5",
    "(1, 2, -3, 0.4, 5)",
    "[1 2 -3 0.4 5]",
    "np.r_[[1, 2, -3, 0.4, 5]]",
    "numpy.asarray(1, 2, -3, 0.4, 5)",
    "np.array([1, 2, -3, 0.4, 5])",
    "array([1, 2, -3, 0.4, 5])",
    "r_[[1, 2, -3, 0.4, 5]]",
    "numpy.array([1, 2, -3, 0.4, 5])",
    "np.asarray([1, 2, -3, 0.4, 5])",
]


class Test_numpy_utils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmpdir = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmpdir)

    def test__numpy_dtypes_dict(self):
        for _key, _val in NUMPY_DTYPES.items():
            if not isinstance(_key, str):
                continue
            with self.subTest(key=_key):
                _ = np.arange(130, dtype=_val)

    def test_parse_string_to_ndarray__simple_cases(self):
        for _input in _SIMPLE_CASES:
            with self.subTest(input=_input):
                _new = NumpyParser(_input)
                self.assertTrue(np.allclose(_new, np.array((1, 2, -3, 0.4, 5))))
        for _input in _SIMPLE_CASES:
            _input = _input.replace("-", "")
            with self.subTest(input=_input):
                _new = NumpyParser(_input)
                self.assertTrue(np.allclose(_new, np.array((1, 2, 3, 0.4, 5))))

    def test_parse_string_to_ndarray__arange(self):
        for _input, _arr in _ARANGE_EXAMPLES:
            with self.subTest(input=_input):
                _new = NumpyParser(_input)
                self.assertTrue(np.allclose(_new, _arr))

    def test_parse_string_to_ndarray__linspace(self):
        for _input, _arr in _LINSPACE_EXAMPLES:
            with self.subTest(input=_input):
                _new = NumpyParser(_input)
                self.assertTrue(np.allclose(_new, _arr))

    def test_parse_string_to_ndarray__illegal_entries(self):
        for _input in [
            "1 'e' 3 5" "npp.array(('a', 1, 12, None))",
            "np.arrrange(5)",
            "npp.arange(1, 4, 5)" "np.arange()",
            "np.arange(1, 2, 3, 4)",
            "np.loadtxt('test.txt', converters='12')",
            "np.loadtxt('dummy/file.name', unpack=True)",
        ]:
            with self.subTest(input=_input), self.assertRaises(UserConfigError):
                NumpyParser(_input)

    def test_parse_string_to_ndarray__loadtxt(self):
        _arr = np.random.rand(40, 33)
        _fname = self._tmpdir.joinpath("test.txt")
        np.savetxt(_fname, _arr)
        for _kwargs in [
            {},
            {"comments": "~"},
            {"skiprows": 3},
            {"usecols": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)},
            {"usecols": [1, 2, 3, 8, 15]},
            {"usecols": {1, 5, 2}},
            {"max_rows": 20},
            {"max_rows": 20, "usecols": [1, 2, 3, 8, 15], "skiprows": 3},
        ]:
            with self.subTest(kwargs=_kwargs):
                _kwargs_str = (", " if len(_kwargs) > 0 else "") + ", ".join(
                    f"{k}=" + (f"'{v}'" if isinstance(v, str) else str(v))
                    for k, v in _kwargs.items()
                )
                _ref = np.loadtxt(_fname, **_kwargs)
                _new = NumpyParser(f"np.loadtxt({_fname}{_kwargs_str})")
                self.assertTrue(np.allclose(_new, _ref))

    def test_parse_string_to_ndarray__loadtxt_delimiters(self):
        _arr = np.random.rand(40, 33)
        _fname = self._tmpdir.joinpath("test.txt")
        np.savetxt(_fname, _arr, delimiter=",")
        _txt = f"np.loadtxt({_fname}, delimiter=',')"
        _ref = np.loadtxt(_fname, delimiter=",")
        _new = NumpyParser(_txt)
        self.assertTrue(np.allclose(_new, _ref))

    def test_parse_string_to_ndarray__load(self):
        _arr = np.random.rand(40, 33)
        _fname = self._tmpdir.joinpath("test.npy")
        np.save(_fname, _arr)
        for _kwargs in [
            {},
            {"mmap_mode": "r"},
            {"mmap_mode": None},
            {"mmap_mode": "r+"},
        ]:
            with self.subTest(kwargs=_kwargs):
                _kwargs_str = (", " if len(_kwargs) > 0 else "") + ", ".join(
                    f"{k}=" + (f"'{v}'" if isinstance(v, str) else str(v))
                    for k, v in _kwargs.items()
                )
                _ref = np.load(_fname, **_kwargs)
                _new = NumpyParser(f"np.load({_fname}{_kwargs_str})")
                self.assertTrue(np.allclose(_new, _ref))

    def __test_parse_string_to_ndarray(self, func: callable, func_name: str):
        for _shape, _value, _kwargs in [
            [5, 12, {}],
            [(5,), 4.3, {}],
            [(5, 2), -4.44e5, {}],
            [(5, 2), 12.4, {"dtype": np.float32}],
            [(5, 2), 44, {"dtype": np.int64}],
            [(5, 2), 1.234e-4, {"dtype": np.float64, "order": "F"}],
            [(5, 2), -5.432e-2, {"dtype": np.float32, "order": "C"}],
            [(5, 2, 7), 6789, {"dtype": np.int64}],
        ]:
            with self.subTest(shape=_shape, kwargs=_kwargs):
                _kwargs_str = (", " if len(_kwargs) > 0 else "") + ", ".join(
                    f"{k}=" + (f"'{v}'" if isinstance(v, str) else f"np.{v.__name__}")
                    for k, v in _kwargs.items()
                )
                if func_name == "full":
                    _ref = func(_shape, _value, **_kwargs)
                    _parse_str = f"np.{func_name}({_shape}, {_value}{_kwargs_str})"
                else:
                    _ref = func(_shape, **_kwargs)
                    _parse_str = f"np.{func_name}({_shape}{_kwargs_str})"
                _new = NumpyParser(_parse_str)
                self.assertTrue(np.allclose(_new, _ref))

    def test_parse_string_to_ndarray__zeros(self):
        self.__test_parse_string_to_ndarray(np.zeros, "zeros")

    def test_parse_string_to_ndarray__ones(self):
        self.__test_parse_string_to_ndarray(np.ones, "ones")

    def test_parse_string_to_ndarray__full(self):
        self.__test_parse_string_to_ndarray(np.full, "full")


if __name__ == "__main__":
    unittest.main()
