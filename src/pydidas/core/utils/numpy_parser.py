# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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

"""
The NumpyParser class is used to create numpy arrays from strings.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["NumpyParser"]


import argparse
import re
from functools import partialmethod

import numpy as np

from pydidas.core.constants import NUMPY_ARGPARSE_ARGS, NUMPY_DTYPES
from pydidas.core.exceptions import UserConfigError


_NUM_NUMERIC_CHARS_TRANSLATE = str.maketrans("", "", "01234567890. ")

BRACKETED_KEY = "$$$BRACKETED$$$"


class _NumpyParser:
    @classmethod
    def _create_parser(cls, func_name: str) -> argparse.ArgumentParser:
        """
        Create an argparse parser for the given numpy function.

        Parameters
        ----------
        func_name : str
            The name of the numpy function.

        Returns
        -------
        argparse.ArgumentParser :
            The argparse parser.
        """
        _parser = argparse.ArgumentParser(add_help=False, prog=func_name)
        for _arg, _kwargs in NUMPY_ARGPARSE_ARGS[func_name].items():
            _parser.add_argument(_arg, **_kwargs)
        return _parser

    def __init__(self):
        self._parsers = {
            _name: self._create_parser(_name) for _name in NUMPY_ARGPARSE_ARGS
        }
        self._supported_funcs = ["r_", "asarray", "array"] + list(self._parsers.keys())

    def __call__(self, input_str: str) -> np.ndarray:
        """
        Call the NumpyParser class and parse the input string.

        Parameters
        ----------
        input_str : str
            The input string to be parsed.

        Returns
        -------
        np.ndarray :
            The parsed ndarray.
        """
        return self.parse_string_to_ndarray(input_str)

    def _parse_known_args(self, input_str: str, func_name: str) -> tuple[dict, list]:
        """
        Parse the known arguments of a numpy function.

        Parameters
        ----------
        input_str : str
            The input string.
        func_name :
            The name of the numpy function.

        Returns
        -------
        dict :
            The parsed known kwargs.
        list :
            The remaining items.
        """
        input_str = input_str[len(func_name) + 1 : -1]
        if len(input_str) == 0:
            raise UserConfigError(
                "The argument string is empty. Please check the input and provide "
                f"arguments for `{func_name}`."
            )
        _kwargs, _other = self._parsers[func_name].parse_known_args(
            self._get_items_as_list(input_str)
        )
        return vars(_kwargs), _other

    @staticmethod
    def _get_items_as_list(input_str: str) -> list[str]:
        """
        Split a string along the commas and return the items as a list.

        Also, keyword arguments will be modified with a leading `--` to be parsed
        by the argparse module.

        Parameters
        ----------
        items : str
            The input string.

        Returns
        -------
        list[str]
            The string, formatted into a list for use in argparse.
        """
        _bracketed = []
        while True:
            _result = re.search(r"\(.*?\)|\[.*?\]|\{.*?\}", input_str)
            if _result is None:
                break
            _bracketed.append(_result.group())
            input_str = input_str.replace(_result.group(), BRACKETED_KEY)
        _items = re.split(",(?=[^\"'])", re.sub(r"\s", "", input_str))
        for _idx, _item in enumerate(_items):
            if BRACKETED_KEY in _item:
                _items[_idx] = _item.replace(BRACKETED_KEY, _bracketed.pop(0), 1)
        return [
            ("--" + item.replace("'", "")) if "=" in item else item for item in _items
        ]

    def parse_string_to_ndarray(self, input_str: str) -> np.ndarray:
        """
        Parse a string to an ndarray.

        Parameters
        ----------
        input_str : str
            The input string.

        Returns
        -------
        np.ndarray
            The output ndarray.
        """
        _raw_input_str = input_str
        try:
            for _item in ["np.", "numpy."]:
                if input_str.startswith(_item):
                    input_str = input_str[len(_item) :]
            for _func in self._supported_funcs:
                if (
                    (input_str.startswith(_func) and input_str.endswith(")"))
                    or input_str.startswith("r_[")
                    and input_str.endswith("]")
                ):
                    _parse_func = getattr(self, f"_parse_{_func}")
                    return _parse_func(input_str)
            return self.__parse_plain_string(input_str)
        except (
            ValueError,
            TypeError,
            UserConfigError,
            KeyError,
            argparse.ArgumentError,
        ):
            raise
        raise UserConfigError(
            f"Could not parse the input string `{_raw_input_str}` to an ndarray."
        )

    @staticmethod
    def __parse_plain_string(
        input_str: str, func_name_length: int = 0, trailing_crop: int = 0
    ) -> np.ndarray:
        """
        Parse a plain string to an ndarray.

        Parameters
        ----------
        input_str : str
            The input string.
        func_name_length : int, optional
            The length of the input function name to crop the input string.
        trailing_crop : int, optional
            The number of chars to be cropped at the end of the input. This option
            is relevant for the `r_` function.

        Returns
        -------
        np.ndarray :
            The output ndarray.
        """
        if func_name_length > 0:
            input_str = input_str[func_name_length + 1 : -1]
        if trailing_crop > 0:
            input_str = input_str[:-trailing_crop]
        if input_str[0] in ["(", "["] and input_str[-1] in [")", "]"]:
            input_str = input_str[1:-1]
        _non_numeric_chars = set(input_str.translate(_NUM_NUMERIC_CHARS_TRANSLATE))
        if _non_numeric_chars in [set("-"), set()]:
            return np.fromstring(input_str, sep=" ")
        if _non_numeric_chars in [set(",-"), set(",")]:
            return np.fromstring(input_str, sep=",")
        raise UserConfigError("Could not parse the given string.")

    _parse_r_ = partialmethod(__parse_plain_string, func_name_length=3, trailing_crop=1)
    _parse_array = partialmethod(__parse_plain_string, func_name_length=5)
    _parse_asarray = partialmethod(__parse_plain_string, func_name_length=7)

    def _parse_arange(self, input_str: str) -> np.ndarray:
        """
        Parse the arguments given for the creation of an arange array.

        Parameters
        ----------
        input_str : str
            The input string.

        Returns
        -------
        np.ndarray :
            The output ndarray.
        """
        _kwargs, _other = self._parse_known_args(input_str, "arange")
        _args = _kwargs.pop("args")
        if len(_args) == 1:
            _kwargs["stop"] = _args.pop(0)
        for _key, _type in (
            ("start", float),
            ("stop", float),
            ("step", float),
            ("dtype", str),
        ):
            if len(_args) > 0:
                _tmp_arg = _args.pop(0)
                if _type is bool:
                    _tmp_arg = _tmp_arg.lower() in ("true", "1")
                _kwargs[_key] = _type(_tmp_arg)
        if _kwargs["dtype"] not in NUMPY_DTYPES:
            raise UserConfigError("Invalid dtype.")
        _kwargs["dtype"] = NUMPY_DTYPES[_kwargs["dtype"]]
        return np.arange(**_kwargs)

    def _parse_linspace(self, input_str: str) -> np.ndarray:
        """
        Parse the arguments given for the creation of a linspace array
        .
        Parameters
        ----------
        input_str : str
            The input string.

        Returns
        -------
        np.ndarray :
            The output ndarray.
        """
        _kwargs, _other = self._parse_known_args(input_str, "linspace")
        _args = _kwargs.pop("args")
        for _argname in ("start", "stop"):
            if abs(_kwargs[_argname] - int(_kwargs[_argname])) < 1e-8:
                _kwargs[_argname] = int(_kwargs[_argname])
        for _key, _type in (
            ("num", int),
            ("endpoint", bool),
            ("retstep", bool),
            ("dtype", str),
            ("axis", int),
        ):
            if len(_args) > 0:
                _tmp_arg = _args.pop(0)
                _kwargs[_key] = (
                    _tmp_arg.lower() in ("true", "1")
                    if _type is bool
                    else _type(_tmp_arg)
                )
        _kwargs["dtype"] = NUMPY_DTYPES[_kwargs["dtype"]]
        if _kwargs["retstep"]:
            raise UserConfigError("Cannot process arrays with `retstep=True`.")
        return np.linspace(_kwargs.pop("start"), _kwargs.pop("stop"), **_kwargs)

    def _parse_loadtxt(self, input_str: str) -> np.ndarray:
        """
        Parse the arguments given for loading a text file with numpy.loadtxt.

        Parameters
        ----------
        input_str : str
            The input string.

        Returns
        -------
        dict :
            A dictionary with the parsed arguments.
        """
        _kwargs, _other = self._parse_known_args(input_str, "loadtxt")
        _fname = _kwargs.pop("fname")
        for _key in ("delimiter", "usecols", "max_rows", "quotechar", "like"):
            _kwargs[_key] = None if _kwargs[_key] == "None" else _kwargs[_key]
        if _kwargs["usecols"] is not None:
            _cols = _kwargs["usecols"].strip("()[]{}")
            _kwargs["usecols"] = tuple(int(col) for col in _cols.split(","))
        if _kwargs["unpack"]:
            raise UserConfigError("Cannot process np.loadtxt with `unpack=True`.")
        for _item in _other:
            if "converters" in _item and _item.split("=")[1] != "None":
                raise UserConfigError("Cannot process np.loadtxt with `converters`.")
        return np.loadtxt(_fname, **_kwargs)

    def _parse_load(self, input_str: str) -> np.ndarray:
        """
        Parse the arguments given for loading a file with numpy.load.

        Parameters
        ----------
        input_str : str
            The input string.

        Returns
        -------
        np.ndarray :
            The output ndarray.
        """
        _kwargs, _other = self._parse_known_args(input_str, "load")
        _fname = _kwargs.pop("fname")
        _kwargs["mmap_mode"] = (
            None if _kwargs["mmap_mode"] == "None" else _kwargs["mmap_mode"]
        )
        return np.load(_fname, **_kwargs)

    def __parse_for_func(
        self, input_str: str, np_func=None, np_func_name=""
    ) -> np.ndarray:
        """
        Parse the arguments given for creating an array of ones or zeros.

        Parameters
        ----------
        input_str : str
            The input string.
        np_func : callable, optional
            The numpy function to be used.
        np_func_name : str, optional
            The function name as string.

        Returns
        -------
        np.ndarray :
            The output ndarray.
        """
        _kwargs, _other = self._parse_known_args(input_str, np_func_name)
        _shape = _kwargs.pop("shape").strip("()").split(",")
        if len(_shape) == 1 or (len(_shape) == 2 and _shape[1] == ""):
            _shape = int(_shape[0])
        else:
            _shape = tuple(int(dim) for dim in _shape)
        _kwargs["dtype"] = NUMPY_DTYPES[_kwargs["dtype"]]
        if "fill_value" in _kwargs:
            _fill_value = float(_kwargs.pop("fill_value"))
            return np_func(_shape, _fill_value, **_kwargs)
        return np_func(_shape, **_kwargs)

    _parse_ones = partialmethod(__parse_for_func, np_func=np.ones, np_func_name="ones")
    _parse_zeros = partialmethod(
        __parse_for_func, np_func=np.zeros, np_func_name="zeros"
    )
    _parse_full = partialmethod(__parse_for_func, np_func=np.full, np_func_name="full")


NumpyParser = _NumpyParser()
