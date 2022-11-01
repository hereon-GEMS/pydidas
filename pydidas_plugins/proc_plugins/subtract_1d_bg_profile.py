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
Module with the Subtract1dBackgroundProfile Plugin which can be used to
subtract a given background profile from a 1-d dataset, e.g. integrated
diffraction data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["Subtract1dBackgroundProfile"]

from pathlib import Path

import numpy as np

from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED
from pydidas.core.utils import process_1d_with_multi_input_dims
from pydidas.core import Parameter, get_generic_param_collection
from pydidas.data_io import import_data
from pydidas.plugins import ProcPlugin


_PARAM_THRESH = Parameter(
    "threshold_low",
    float,
    None,
    allow_None=True,
    name="Lower threshold",
    tooltip=(
        "The lower threhold. Any values in the corrected"
        " dataset smaller than the threshold will be set "
        "to the threshold value."
    ),
)

_PARAM_PROFILE_FILE = Parameter(
    "profile_file",
    Path,
    Path(),
    name="Filename of profile file",
    tooltip=("The filename of the file with the background profile."),
)


class Subtract1dBackgroundProfile(ProcPlugin):
    """
    Subtract a given background profile from 1-d data.

    This plugin simple substracts the given profile from all datasets. A
    lower threshold can be given, for example to prevent negative values.
    """

    plugin_name = "Subtract 1D background profile"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_INTEGRATED
    default_params = get_generic_param_collection("process_data_dim")
    default_params.add_params(_PARAM_THRESH.get_copy(), _PARAM_PROFILE_FILE.get_copy())
    input_data_dim = 1
    output_data_dim = 1
    output_data_label = "Background-corrected data"
    output_data_unit = "a.u."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thresh = None

    def pre_execute(self):
        """
        Set-up the fit and store required values.
        """
        self._thresh = self.get_param_value("threshold_low")
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None

        _fname = self.get_param_value("profile_name")
        _profile = import_data(_fname)

        self._profile = _profile

    @process_1d_with_multi_input_dims
    def execute(self, data, **kwargs):
        """
        Subtract a one-dimensional background profile.

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data .
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        data = data - self._profile

        if self._thresh is not None:
            _indices = np.where(data < self._thresh)[0]
            data[_indices] = self._thresh

        return data, kwargs
