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

"""
Module with format_arguments function which takes *args and **kwargs and
converts them into an argparse-compatible list.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["format_arguments"]


import re
from typing import List


def format_arguments(*args: tuple, **kwargs: dict) -> List[str]:
    """
    Convert arguments to an argpare-compatible list.

    This function accepts arguments and keyword arguments and converts them.

    Parameters
    ----------
    args : tuple
        Input arguments.
    kwargs : dict
        Keyword arguments.

    Returns
    -------
    list
        An argparse-compatible list.
    """
    _new_args = []
    for item, key in kwargs.items():
        if key is True:
            _new_args.append(f"--{item}")
        else:
            _new_args.append(f"-{item}")
            _new_args.append(key if isinstance(key, str) else str(key))

    for arg in args:
        arg = arg if isinstance(arg, str) else str(arg)
        if "=" in arg or " " in arg:
            _split_args = [item for item in re.split(" |=", arg) if item != ""]
            if not _split_args[0].startswith("-"):
                _split_args[0] = f"-{_split_args[0]}"
            _new_args += _split_args
        else:
            _new_args.append(arg)
    return _new_args
