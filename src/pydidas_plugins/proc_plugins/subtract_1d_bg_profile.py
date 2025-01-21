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
Module with the Subtract1dBackgroundProfile Plugin which can be used to
subtract a given background profile from a 1-d dataset, e.g. integrated
diffraction data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Subtract1dBackgroundProfile"]


from pathlib import Path
from typing import Union

import numpy as np

from pydidas.core import Dataset, Parameter, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN_INTEGRATED
from pydidas.core.utils import process_1d_with_multi_input_dims
from pydidas.data_io import import_data
from pydidas.plugins import ProcPlugin


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
    plugin_subtype = PROC_PLUGIN_INTEGRATED

    default_params = get_generic_param_collection(
        "process_data_dim", "threshold_low", "multiplicator"
    )
    default_params.add_param(_PARAM_PROFILE_FILE.copy())

    input_data_dim = 1
    output_data_dim = 1
    output_data_label = "Background-corrected data"
    output_data_unit = "a.u."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thresh = None

    def pre_execute(self):
        """
        Set up the fit and store required values.
        """
        self._thresh = self.get_param_value("threshold_low")
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None

        _fname = self.get_param_value("profile_name")
        self._profile = import_data(_fname)
        if self.get_param_value("multiplicator") != 1.0:
            self._profile *= self.get_param_value("multiplicator")

    @process_1d_with_multi_input_dims
    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
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
        data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        data = data - self._profile
        if self._thresh is not None:
            _indices = np.where(data < self._thresh)[0]
            data[_indices] = self._thresh
        return data, kwargs
