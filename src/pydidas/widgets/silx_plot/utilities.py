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

__author__ = "Malte Storm, Nonni Heere"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_allowed_kwargs"]


import inspect
from typing import Any, Callable

import numpy as np

from pydidas.core import Dataset, PydidasQsettings, UserConfigError
from pydidas_qtcore import PydidasQApplication


_ALLOWED_KWARGS = {}
_QSETTINGS = PydidasQsettings()


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
    Check if the given axis is structured in columns rather than continuous
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
    PydidasQApplication.instance().set_status_message(
        f"Warning: Axis {axis} does not contain columns. Labels may be incorrect."
    )
    return data.get_axis_description(axis).split(";")


def check_data_dimensions(data: Dataset | np.ndarray, target_dim: int) -> None:
    """
    Check the data dimensions.

    Parameters
    ----------
    data : Dataset or np.ndarray
        The data to display.
    """
    if data.ndim == target_dim:
        return
    if target_dim == 1 and data.ndim == 2:
        _n_max: int = _QSETTINGS.value("user/max_number_curves", int)  # type: ignore[assignment]
        if data.shape[0] > _n_max:
            raise UserConfigError(
                f"The number of given curves ({data.shape[0]}) exceeds the "
                f"maximum number of curves allowed ({_n_max}).\n"
                "Please limit the data range to be displayed or increase the "
                "maximum number of curves in the user settings (Options -> "
                "User config). Please note that displaying a large number of "
                "curves will slow down the plotting performance."
            )
        return
    if data.ndim != target_dim:
        raise UserConfigError(
            f"The given dataset has {data.ndim} dimensions. Please check the "
            f"input data definition:\nThe expected input is {target_dim} "
            "dimensions."
        )
