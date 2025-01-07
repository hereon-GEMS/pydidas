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
The colors module holds color names and RGB codes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "NUMPY_HUMAN_READABLE_DATATYPES",
    "NUMPY_DTYPES",
    "NUMPY_ARGPARSE_ARGS",
]

import argparse

import numpy as np


def _string2bool(input_str: str) -> bool:
    """
    Return the boolean value from a string input.

    Parameters
    ----------
    input_str : str
        The input string.

    Returns
    -------
    bool :
        The corresponding boolean value.
    """
    if isinstance(input_str, bool):
        return input_str
    input_str = input_str.strip()
    if input_str.lower() not in ("true", "1", "false", 0):
        raise argparse.ArgumentTypeError("Boolean value expected.")
    return input_str.lower() in ("true", "1")


NUMPY_HUMAN_READABLE_DATATYPES = {
    "boolean (1 bit integer)": np.bool_,
    "float 16 bit": np.half,
    "float 32 bit": np.single,
    "float 64 bit": np.double,
    "float 128 bit": np.longdouble,
    "int 8 bit": np.int8,
    "int 16 bit": np.int16,
    "int 32 bit": np.int32,
    "int 64 bit": np.int64,
    "unsigned int 8 bit": np.uint8,
    "unsigned int 16 bit": np.uint16,
    "unsigned int 32 bit": np.uint32,
    "unsigned int 64 bit": np.uint64,
}


NUMPY_DTYPES = {k: v for k, v in np.sctypeDict.items() if issubclass(v, np.number)}
NUMPY_DTYPES.update(
    {f"np.{key}": value for key, value in NUMPY_DTYPES.items() if key == value.__name__}
    | {None: None, "None": None, "int": int, "float": float}
)

NUMPY_ARGPARSE_ARGS = {
    "arange": {
        "args": {"type": float, "help": "args", "nargs": "*"},
        "--dtype": {"type": str, "help": "dtype", "default": None},
    },
    "linspace": {
        "start": {"type": float, "help": "start"},
        "stop": {"type": float, "help": "stop"},
        "args": {"type": str, "help": "args", "nargs": "*"},
        "--num": {"type": int, "help": "num", "default": 50},
        "--endpoint": {"type": _string2bool, "help": "endpoint", "default": True},
        "--retstep": {"type": _string2bool, "help": "retstep", "default": False},
        "--dtype": {"type": str, "help": "dtype", "default": None},
        "--axis": {"type": int, "help": "axis", "default": 0},
    },
    "loadtxt": {
        "fname": {"type": str, "help": "fname"},
        "--dtype": {"type": str, "help": "dtype", "default": float},
        "--comments": {"type": str, "help": "comments", "default": "#"},
        "--delimiter": {"type": str, "help": "delimiter", "default": None},
        "--skiprows": {"type": int, "help": "skiprows", "default": 0},
        "--usecols": {"type": str, "help": "usecols", "default": None},
        "--unpack": {"type": _string2bool, "help": "unpack", "default": False},
        "--ndmin": {"type": int, "help": "ndmin", "default": 0},
        "--encoding": {"type": str, "help": "encoding", "default": "bytes"},
        "--max_rows": {"type": int, "help": "max_rows", "default": None},
        "--quotechar": {"type": str, "help": "quotechar", "default": None},
        "--like": {"type": str, "help": "like", "default": None},
    },
    "load": {
        "fname": {"type": str, "help": "fname"},
        "--mmap_mode": {"type": str, "help": "mmap_mode", "default": None},
        "--encoding": {"type": str, "help": "encoding", "default": "ASCII"},
    },
    "ones": {
        "shape": {"type": str, "help": "shape"},
        "--dtype": {"type": str, "help": "dtype", "default": None},
        "--order": {"type": str, "help": "order", "default": "C"},
    },
    "zeros": {
        "shape": {"type": str, "help": "shape"},
        "--dtype": {"type": str, "help": "dtype", "default": "float"},
        "--order": {"type": str, "help": "order", "default": "C"},
    },
    "full": {
        "shape": {"type": str, "help": "shape"},
        "fill_value": {"type": float, "help": "fill_value"},
        "--dtype": {"type": str, "help": "dtype", "default": None},
        "--order": {"type": str, "help": "order", "default": "C"},
    },
}
