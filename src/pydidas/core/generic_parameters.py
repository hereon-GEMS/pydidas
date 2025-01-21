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
This module includes functions to create generic Parameters and ParameterCollections.

Reference keys are defined in the core.generic_params subpackage.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_generic_parameter", "get_generic_param_collection"]


from collections.abc import Iterable
from pathlib import Path

from pydidas.core.generic_params import GENERIC_PARAMS_METADATA
from pydidas.core.hdf5_key import Hdf5key
from pydidas.core.parameter import Parameter
from pydidas.core.parameter_collection import ParameterCollection


def get_generic_parameter(refkey: str) -> Parameter:
    """
    Create a Parameter from a refkey based on pre-defined information.

    Parameters
    ----------
    refkey : str
        The reference key of the generic Parameter.

    Raises
    ------
    KeyError
        If not description is provided for the given refkey.

    Returns
    -------
    pydidas.core.Parameter
        A Parameter object.
    """
    try:
        _config = GENERIC_PARAMS_METADATA[refkey].copy()
    except KeyError as _ke:
        raise KeyError(
            f'No Parameter with the reference key "{refkey}" '
            "in the GENERIC_PARAM_DESCRIPTION collection."
        ) from _ke
    match _config["type"]:
        case "Path":
            _config["type"] = Path
            _config["default"] = Path(_config["default"])
        case "Hdf5key":
            _config["type"] = Hdf5key
            _config["default"] = Hdf5key(_config["default"])
    _type = _config.pop("type")
    _default = _config.pop("default")
    return Parameter(refkey, _type, _default, **_config)


def get_generic_param_collection(
    *param_keys: Iterable[str, ...],
) -> ParameterCollection:
    """
    Get an initialized ParameterCollection from a number of generic Parameter keys.

    Parameters
    ----------
    *param_keys : str
        Any number of Parameter keys referenced as a generic Parameter.

    Returns
    -------
    pydidas.core.ParameterCollection
        The initialized ParameterCollection with a new set of Parameters based
        on the supplied keys.
    """
    _params = [get_generic_parameter(_param) for _param in param_keys]
    return ParameterCollection(*_params)
