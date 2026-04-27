# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_allowed_kwargs", "axis_is_columns", "get_column_labels"]


import inspect
from typing import Any, Callable

from pydidas.core import Dataset


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


def axis_is_columns(axis: int, data: Dataset) -> bool:
    """
    Check if the given axis is structured in columns rather than continous
    data. This is not a definitive check, it just looks at the axis labels.

    Parameters
    ----------
    axis : int
        The axis index to check.
    data : Dataset
        The dataset to check.

    Returns
    -------
    bool
        True if the axis is structured in columns rather than continous data
    """
    axis_label = data.get_axis_description(axis)
    if ";" in axis_label:
        column_labels = axis_label.split(";")
        if len(column_labels) != data.shape[axis]:
            return False
        colon_in_label = True
        for label in column_labels:
            if ":" not in label:
                colon_in_label = False
        return colon_in_label
    return False


def get_column_labels(axis: int, data: Dataset) -> list[str]:
    """
    Get the column labels for the given axis. Assumes the axis is structured
    in columns.

    Parameters
    ----------
    axis : int
        The axis index to get the column labels for.
    data : Dataset
        The dataset to get the column labels from.

    Returns
    -------
    list[str]
        The column labels for the given axis.
    """
    if axis_is_columns(axis, data):
        return [
            part.split(":", 1)[1].strip()
            for part in data.get_axis_description(axis).split(";")
        ]
    raise ValueError(f"Axis {axis} does not contain columns.")
