# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the SubtractBackgroundImage Plugin which can be used to subtract
another image as background.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SubtractBackgroundImage"]

import os

import numpy as np

from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_IMAGE
from pydidas.core.utils import rebin2d
from pydidas.data_io import import_data
from pydidas.plugins import ProcPlugin
from pydidas.widgets.plugin_config_widgets import SubtractBackgroundImageConfigWidget


class SubtractBackgroundImage(ProcPlugin):
    """
    Subtract a background image from the data.
    """

    plugin_name = "Subtract background image"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_IMAGE
    default_params = get_generic_param_collection(
        "bg_file", "bg_hdf5_key", "bg_hdf5_frame", "threshold_low", "multiplicator"
    )
    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Background corrected image"
    output_data_unit = "counts"
    has_unique_parameter_config_widget = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bg_image = None
        self._thresh = None

    def pre_execute(self):
        """
        Load the background image.
        """
        _bg_fname = self.get_param_value("bg_file")
        if not os.path.isfile(_bg_fname):
            raise UserConfigError(
                f'The filename "{_bg_fname}" does not point to a valid file. Please '
                "verify the path."
            )
        self._bg_image = import_data(
            _bg_fname,
            dataset=self.get_param_value("bg_hdf5_key"),
            frame=self.get_param_value("bg_hdf5_frame"),
        )
        if self.get_param_value("multiplicator") != 1.0:
            self._bg_image *= self.get_param_value("multiplicator")
        self._thresh = self.get_param_value("threshold_low")
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None

    def execute(self, data, **kwargs):
        """
        Apply a mask to an image (2d data-array).

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
        if data.shape != self._bg_image.shape:
            _roi, _binning = self.get_single_ops_from_legacy()
            self._bg_image = rebin2d(self._bg_image[_roi], _binning)
        _corrected_data = data - self._bg_image
        if self._thresh is not None:
            _corrected_data[_corrected_data < self._thresh] = self._thresh
        return _corrected_data, kwargs

    def get_parameter_config_widget(self):
        """
        Get the unique configuration widget associated with this Plugin.

        Returns
        -------
        QtWidgets.QWidget
            The unique ParameterConfig widget
        """
        return SubtractBackgroundImageConfigWidget(self)
