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

"""
Module with format_arguments functions which takes *args and **kwargs and
converts them into an argparse-compatible list.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['format_arguments']

import re


def format_arguments(*args, **kwargs):
    """
    Function which accepts arguments and keyword arguments and converts
    them to a argparse-compatible list.
    """
    _new_args = []
    for item, key in kwargs.items():
        if key is True:
            _new_args.append(f'--{item}')
        else:
            _new_args.append(f'-{item}')
            _new_args.append(key if isinstance(key, str) else str(key))

    for arg in args:
        arg = arg if isinstance(arg, str) else str(arg)
        if '=' in arg or ' ' in arg:
            _split_args = [item for item in re.split(' |=', arg) if item != '']
            if not _split_args[0].startswith('-'):
                _split_args[0] = f'-{_split_args[0]}'
            _new_args += _split_args
        else:
            _new_args.append(arg)
    return _new_args
