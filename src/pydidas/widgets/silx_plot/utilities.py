# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with utilities for silx_plot package files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_allowed_kwargs"]


import inspect
from typing import Any, Callable


_ALLOWED_KWARGS = {}


def get_allowed_kwargs(method: Callable, kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Filter a kwargs dictionary to only include those kwargs allowed for a method.

    Parameters
    ----------
    method : Callable
        The method to inspect for allowed kwargs.
    kwargs : dict[str, Any]
        The input keyword arguments.

    Returns
    -------
    dict[str, Any]
        The filtered keyword arguments.
    """
    if _ALLOWED_KWARGS.get(method) is None:
        _params = inspect.signature(method).parameters
        _ALLOWED_KWARGS[method] = [
            _key
            for _key, _value in _params.items()
            if _value.default is not inspect.Parameter.empty
        ]
    _whitelist = _ALLOWED_KWARGS[method]
    return {_key: _val for _key, _val in kwargs.items() if _key in _whitelist}
