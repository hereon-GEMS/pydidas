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
Module with the SubtractBackgroundImage Plugin which can be used to subtract
another image as background.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SubtractBackgroundImage"]


import os
from typing import Union

import numpy as np
from qtpy import QtCore

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.constants import HDF5_EXTENSIONS, PROC_PLUGIN_IMAGE
from pydidas.core.utils import get_extension
from pydidas.data_io import import_data
from pydidas.plugins import ProcPlugin
from pydidas.widgets.plugin_config_widgets import (
    GenericPluginConfigWidget,
)


class SubtractBackgroundImage(ProcPlugin):
    """
    Subtract a background image from the data.

    A new threshold for the resulting image can be defined, for example to prevent
    negative values.

    Another option is to apply a multiplicator to the background image, for example
    to correct for different exposure times or high sample absorption which reduces
    the background.
    """

    plugin_name = "Subtract background image"
    plugin_subtype = PROC_PLUGIN_IMAGE

    default_params = get_generic_param_collection(
        "bg_file",
        "bg_hdf5_key",
        "bg_hdf5_frame",
        "threshold_low",
        "multiplicator",
        "use_roi",
        "roi_xlow",
        "roi_xhigh",
        "roi_ylow",
        "roi_yhigh",
        "binning",
    )
    advanced_parameters = [
        "use_roi",
        "roi_xlow",
        "roi_xhigh",
        "roi_ylow",
        "roi_yhigh",
        "binning",
    ]
    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Background corrected image"
    output_data_unit = "counts"
    has_unique_parameter_config_widget = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bg_image = None
        self._thresh = None
        self.params["multiplicator"]._Parameter__meta["tooltip"] = (
            "The multiplication scaling factor to be applied to the background image "
            "before subtracting it from the input data."
        )

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
            indices=[0],
            binning=self.get_param_value("binning"),
            roi=self._get_own_roi(),
        )
        if self.get_param_value("multiplicator") != 1.0:
            self._bg_image *= self.get_param_value("multiplicator")
        self._thresh = self.get_param_value("threshold_low")
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None

    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
        """
        Subtract a background image from the input data.

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data .
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _corrected_data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if data.shape != self._bg_image.shape:
            raise UserConfigError(
                "The background image and the data have different shapes. Please check "
                "the input data and the background image.\n"
                f"Input data: {data.shape}\nBackground image: {self._bg_image.shape}"
            )
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
        return SubtractBackgroundImageConfigWidget


class SubtractBackgroundImageConfigWidget(GenericPluginConfigWidget):
    """
    Configuration widget to subtract a background image from the data.

    This widget displays or hides the configuration fields of the hdf5
    dataset based on the file extension of the selected file.
    """

    def connect_signals(self):
        """Connect the signals of the widgets to the appropriate slots."""
        GenericPluginConfigWidget.connect_signals(self)
        self.param_composite_widgets["bg_file"].io_edited.connect(
            self._toggle_hdf5_plugin_visibility
        )

    def finalize_init(self):
        self._toggle_hdf5_plugin_visibility(self.plugin.get_param_value("bg_file"))

    @QtCore.Slot(str)
    def _toggle_hdf5_plugin_visibility(self, new_file: str):
        """
        Toggle the visibility of the plugins for Hdf5 dataset and frame number.

        Parameters
        ----------
        new_file : str
            The filename of the newly selected file.
        """
        _visibility = get_extension(new_file) in HDF5_EXTENSIONS
        self.toggle_param_widget_visibility("bg_hdf5_key", _visibility)
        self.toggle_param_widget_visibility("bg_hdf5_frame", _visibility)

    def update_edits(self):
        """
        Update the configuration fields of the plugin.
        """
        GenericPluginConfigWidget.update_edits(self)
        self._toggle_hdf5_plugin_visibility(self.plugin.get_param_value("bg_file"))
