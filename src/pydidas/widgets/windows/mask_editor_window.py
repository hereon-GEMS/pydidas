# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the MaskEditorWindow class which is a wrapper window to use the pyFAI
mask editor in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MaskEditorWindow"]


from qtpy import QtCore, QtWidgets

from pydidas.core import get_generic_param_collection
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH
from pydidas.core.utils import update_size_policy
from pydidas.data_io import import_data
from pydidas.widgets import parameter_config, silx_plot
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.misc import SelectImageFrameWidget


class MaskEditorWindow(PydidasWindow):
    """
    Window with a simple dialogue to select a number of files and
    """

    show_frame = False
    default_params = get_generic_param_collection(
        "filename", "hdf5_key", "hdf5_frame", "hdf5_slicing_axis"
    )

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="Average images", **kwargs)
        self.setWindowTitle("Mask editor")

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_any_widget(
            "param_frame",
            parameter_config.ParameterEditCanvas,
            font_metric_width_factor=0.8 * FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(0, 0, 1, 1),
        )
        self.create_label(
            "title",
            "Input reference file (not the mask)",
            fontsize_offset=1,
            font_metric_width_factor=0.8 * FONT_METRIC_PARAM_EDIT_WIDTH,
            bold=True,
            parent_widget=self._widgets["param_frame"],
        )
        self.add_any_widget(
            "file_selector",
            SelectImageFrameWidget(*self.params.values()),
            font_metric_width_factor=0.8 * FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget=self._widgets["param_frame"],
        )
        self.create_spacer(None, parent_widget=self._widgets["param_frame"])
        self.create_label(
            "title",
            "Mask parameters",
            fontsize_offset=1,
            bold=True,
            font_metric_width_factor=0.5 * FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget=self._widgets["param_frame"],
        )

        self.create_any_widget("plot_2d", silx_plot.PydidasPlot2D, gridPos=(0, 1, 2, 1))
        update_size_policy(self._widgets["plot_2d"], horizontalStretch=1)

        self._widgets["mask_tools"] = silx_plot.PydidasMaskToolsWidget(
            self, plot=self._widgets["plot_2d"]
        )
        self._widgets["mask_tools"].setDirection(QtWidgets.QBoxLayout.TopToBottom)
        self._widgets["mask_tools"].setMultipleMasks("single")
        self.add_any_widget(
            "mask_tools", self._widgets["mask_tools"], gridPos=(1, 0, 1, 1)
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._widgets["file_selector"].sig_new_file_selection.connect(
            self._open_new_file
        )

    @QtCore.Slot(str, dict)
    def _open_new_file(self, fname: str, input_options: dict):
        """
        Open a new file in the plot window.

        Parameters
        ----------
        fname : str
            The filename of the image file.
        input_options : dict
            Any additional input options.
        """
        _data = import_data(fname, **input_options)
        self._widgets["plot_2d"].addImage(_data)
