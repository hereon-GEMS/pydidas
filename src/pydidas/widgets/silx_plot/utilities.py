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
__all__ = ["check_data_dimensions", "get_allowed_kwargs"]


import inspect
from typing import Any, Callable

import numpy as np

from pydidas.core import Dataset, PydidasQsettings, UserConfigError


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
    if data.ndim > target_dim:
        raise UserConfigError(
            f"The given dataset has {data.ndim} dimensions. Please check the "
            f"input data definition:\nThe expected input is {target_dim} "
            "dimensions."
        )
