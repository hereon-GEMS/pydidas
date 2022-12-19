# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
This module includes functions to create generic Parameters and
ParameterCollections from reference keys defined in the core.constants
subpackage.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["get_generic_parameter", "get_generic_param_collection"]

from pathlib import Path

from .constants.generic_params import GENERIC_PARAMS_METADATA
from .parameter import Parameter
from .parameter_collection import ParameterCollection
from .hdf5_key import Hdf5key


def get_generic_parameter(refkey):
    """
    Create a Parameter based on pre-defined information about the Parameter
    description.

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
    if _config["type"] == "Path":
        _config["type"] = Path
        _config["default"] = Path(_config["default"])
    if _config["type"] == "Hdf5key":
        _config["type"] = Hdf5key
        _config["default"] = Hdf5key(_config["default"])
    _type = _config.pop("type")
    _default = _config.pop("default")
    return Parameter(refkey, _type, _default, **_config)


def get_generic_param_collection(*param_keys):
    """
    Get a initialized ParameterCollection from a number of generic Parameter
    keys.

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
