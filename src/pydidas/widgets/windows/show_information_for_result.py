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
Module with the ShowInformationForResult class which is a widget to display detailed
information about a datapoint from a pydidas result.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ShowInformationForResult"]


from pathlib import Path

from qtpy import QtCore, QtWidgets

from pydidas.core import UserConfigError
from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH
from pydidas.core.utils import ShowBusyMouse, get_fixed_length_str
from pydidas.plugins import BasePlugin
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.misc import ReadOnlyTextWidget
from pydidas.widgets.silx_plot import PydidasPlotStack


class ShowInformationForResult(PydidasWindow, CreateWidgetsMixIn):
    """Window to display detailed information about a result datapoint."""

    show_frame = False
    sig_closed = QtCore.Signal()
    sig_this_frame_activated = QtCore.Signal()

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, **kwargs)
        CreateWidgetsMixIn.__init__(self)

        self.setWindowTitle("Information for data point")
        self._frame = None
        self._loader_plugin = None
        self.create_label(
            "label_title",
            "Information for selected data point:",
            bold=True,
            fontsize_offset=4,
            gridPos=(0, 0, 1, 2),
        )
        self.create_empty_widget("filename_container", gridPos=(-1, 0, 1, 2))
        self.create_label(
            "label_filename",
            "Filename:",
            bold=True,
            font_metric_width_factor=FONT_METRIC_CONFIG_WIDTH,
            parent_widget="filename_container",
        )
        self.create_lineedit(
            "edit_filename",
            parent_widget="filename_container",
            readOnly=True,
        )
        self.create_any_widget(
            "info_field",
            ReadOnlyTextWidget,
            font_metric_width_factor=FONT_METRIC_CONFIG_WIDTH,
            minimumHeight=300,
        )
        self.create_button(
            "but_show_input",
            "Show input frame",
            clicked=self.show_input_image,
            font_metric_width_factor=FONT_METRIC_CONFIG_WIDTH,
            gridPos=(-1, 0, 1, 1),
        )
        self.create_any_widget(
            "plot",
            PydidasPlotStack,
            visible=False,
            minimumHeight=600,
            minimumWidth=600,
            gridPos=(2, 1, self.layout().rowCount() - 2, 1),
        )
        QtWidgets.QApplication.instance().sig_font_metrics_changed.connect(
            self.process_new_font_metrics
        )
        self.layout().setColumnStretch(1, 1)

    def display_information(
        self,
        position: tuple,
        active_dims: tuple,
        selected_indices: list,
        result_metadata: dict,
        loader_plugin: BasePlugin,
        use_timeline: bool = False,
    ):
        """
        Display the information about the selected datapoint.

        Parameters
        ----------
        position : tuple
            A 2-tuple with the data position selected in the image.
        active_dims : tuple
            A 2-tuple with the active dimensions of the selection,
            i.e. the dimensions in which the position is defined.
        selected_indices : list
            The selected indices of the full result dataset. This will be integers
            for inactive dimensions and None for the active dimensions.
        result_metadata : dict
            The metadata of the results.
        loader_plugin : pydidas.plugins.BaseInputPlugin
            The input plugin associated with the results. Required to display the
            input image.
        use_timeline : bool
            If True, the timeline index will be used to get the frame index.
        """
        self._loader_plugin = loader_plugin.copy()
        self._loader_plugin.update_filename_string()
        _scan = self._loader_plugin._SCAN
        _ax_ranges = result_metadata["axis_ranges"]
        _index_y = (abs(_ax_ranges[active_dims[0]] - position[1])).argmin()
        selected_indices[active_dims[0]] = _index_y
        _index_x = (abs(_ax_ranges[active_dims[1]] - position[0])).argmin()
        selected_indices[active_dims[1]] = _index_x

        _info_str = "Selected data position:\n" + "\n".join(
            get_fixed_length_str(
                f"{result_metadata['axis_labels'][_dim]}:", 18, final_space=False
            )
            + get_fixed_length_str(
                _ax_ranges[_dim][_index], 12, formatter="{:.5f}", fill_back=False
            )
            + f" {result_metadata['axis_units'][_dim]}"
            for _dim, _index in enumerate(selected_indices)
        )
        self._frame = (
            selected_indices[0]
            if use_timeline
            else _scan.get_frame_from_indices(selected_indices[: _scan.ndim])
        )
        self._index = _scan.get_index_of_frame(self._frame)
        _scan_indices = _scan.get_frame_position_in_scan(self._frame)

        _info_str += (
            "\n\nPosition in scan:"
            + "\n"
            + get_fixed_length_str("Frame index:", 20, final_space=False)
            + get_fixed_length_str(self._frame, 6, fill_back=False, formatter="{:d}")
            + "\n"
            + "\n".join(
                get_fixed_length_str(f"Scan dim {_dim} index:", 20, final_space=False)
                + get_fixed_length_str(_index, 6, fill_back=False, formatter="{:d}")
                for _dim, _index in enumerate(_scan_indices)
            )
        )
        if "_counted_images_per_file" in loader_plugin.params:
            _index = self._frame % loader_plugin.get_param_value(
                "_counted_images_per_file"
            )
            _info_str += (
                "\n\n" + get_fixed_length_str("Frame in file:", 18) + str(_index)
            )
        self._widgets["info_field"].setText(_info_str)
        self._widgets["edit_filename"].setText(loader_plugin.get_filename(self._frame))
        self._widgets["but_show_input"].setEnabled(True)
        self._widgets["plot"].setVisible(False)
        self.show()

    @QtCore.Slot()
    def show_input_image(self):
        """Show the input image as loaded from the loader plugin."""
        if not Path(self._loader_plugin.get_filename(self._frame)).is_file():
            self._widgets["but_show_input"].setEnabled(False)
            raise UserConfigError(
                "Cannot display the input image because the filename does not point to "
                "a valid file on this system."
            )
        self._widgets["plot"].setVisible(True)
        with ShowBusyMouse():
            self._loader_plugin.pre_execute()
            _input, _kwargs = self._loader_plugin.execute(self._index)
            self._widgets["plot"].plot_data(_input)

    @QtCore.Slot()
    def process_new_font_metrics(self):
        """
        Process the user input of the new font size.
        """
        self.adjustSize()
